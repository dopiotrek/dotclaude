#!/usr/bin/env python3
"""Extract correction-signal messages from Claude Code session transcripts.

Scans ~/.claude/projects/**/*.jsonl (or --claude-dir override), takes the N most
recently modified sessions, and emits a compact JSON of user messages that look
like corrections, plus light context. Deterministic pre-filter so the LLM never
has to read full transcripts.

Usage:
    python3 extract_corrections.py [--claude-dir ~/.claude] [--sessions 50] [--out corrections.json]
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Signals that a user message is correcting / redirecting the agent.
CORRECTION_PATTERNS = [
    r"^no[,.! ]",
    r"^nope\b",
    r"^stop\b",
    r"^wait\b",
    r"^wrong\b",
    r"^not\b",
    r"\bdon'?t\b",
    r"\bdo not\b",
    r"\bnever\b",
    r"\bstop (doing|using|adding|creating)\b",
    r"\bi (told|said|asked)\b",
    r"\bagain\b.*\b(same|still)\b|\b(same|still)\b.*\bagain\b",
    r"\bactually\b",
    r"\binstead\b",
    r"\bwhy (did|are|would) you\b",
    r"\brevert\b",
    r"\bundo\b",
    r"\bthat'?s (not|wrong|incorrect)\b",
    r"\byou (broke|deleted|removed|ignored|missed|forgot|didn'?t)\b",
    r"\buse .+ not .+\b",
    r"\bshould (have|be|use)\b",
    r"\bplease (just|stop|don'?t)\b",
    r"\bnot what i\b",
    r"\bre-?read\b",
    r"\bstill (broken|failing|wrong|not)\b",
]
COMPILED = [re.compile(p, re.IGNORECASE) for p in CORRECTION_PATTERNS]

INTERRUPT_MARKERS = (
    "[Request interrupted by user",
)

# Terse approvals — a short message after an assistant action that matches one
# of these is consent, not correction.
APPROVAL_RX = re.compile(
    r"^(ok(ay)?|yes|yep|sure|thanks?|thank you|perfect|great|nice|good|lgtm|"
    r"looks good.*|ship it.*|go ahead.*|continue.*|proceed.*|sounds good.*|done|cool)[.!]?$",
    re.IGNORECASE,
)
TERSE_LIMIT = 80  # chars; terse-after-action heuristic

MAX_MSG_CHARS = 600          # truncate long user messages
MAX_CTX_CHARS = 200          # truncate assistant context snippet
MAX_HITS_PER_SESSION = 40    # safety cap


def text_of(content):
    """Extract plain text from a message content (string or block array)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return ""


def is_noise(text):
    """Skip slash-command wrappers, hook output, empty, and pasted blobs."""
    if not text.strip():
        return True
    if "<command-name>" in text or "<local-command-stdout>" in text:
        return True
    if text.startswith("Caveat:"):
        return True
    return False


def is_correction(text):
    t = text.strip()
    if any(m in t for m in INTERRUPT_MARKERS):
        return True, "interrupt"
    for rx in COMPILED:
        if rx.search(t):
            return True, "pattern"
    return False, None


def scan_session(path):
    hits = []
    cwd = None
    user_msgs = 0
    last_assistant = ""
    after_assistant = False  # previous main-thread event was an assistant turn
    interrupted = False  # previous event was an interruption marker
    first_ts = last_ts = None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("isSidechain"):
                    continue  # subagent traffic, not the human
                if cwd is None and ev.get("cwd"):
                    cwd = ev["cwd"]
                if ev.get("timestamp"):
                    last_ts = ev["timestamp"]
                    if first_ts is None:
                        first_ts = last_ts
                etype = ev.get("type")
                msg = ev.get("message") or {}
                if etype == "assistant":
                    at = text_of(msg.get("content"))
                    if at:
                        last_assistant = at[-MAX_CTX_CHARS:]
                    after_assistant = True
                    continue
                if etype != "user" or ev.get("isMeta"):
                    continue
                content = msg.get("content")
                # skip pure tool_result user events
                if isinstance(content, list) and all(
                    isinstance(b, dict) and b.get("type") == "tool_result" for b in content
                ):
                    continue
                text = text_of(content)
                if is_noise(text):
                    continue
                if any(m in text for m in INTERRUPT_MARKERS):
                    interrupted = True
                    continue
                user_msgs += 1
                flagged, kind = is_correction(text)
                # a short directive right after an interrupt is a correction
                if interrupted and len(text) < 400:
                    flagged, kind = True, "post-interrupt"
                # terse non-approval right after an assistant turn — e.g.
                # "pnpm. always pnpm." — is usually the user yanking the wheel
                if (not flagged and after_assistant
                        and len(text.strip()) <= TERSE_LIMIT
                        and not APPROVAL_RX.match(text.strip())):
                    flagged, kind = True, "terse-after-action"
                interrupted = False
                after_assistant = False
                if flagged and len(hits) < MAX_HITS_PER_SESSION:
                    hits.append({
                        "msg": text[:MAX_MSG_CHARS],
                        "kind": kind,
                        "ctx": last_assistant,
                        "ts": ev.get("timestamp"),
                    })
    except OSError as e:
        print(f"warn: cannot read {path}: {e}", file=sys.stderr)
    return hits, cwd, user_msgs, first_ts, last_ts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--claude-dir", default=str(Path.home() / ".claude"))
    ap.add_argument("--sessions", type=int, default=50)
    ap.add_argument("--out", default="corrections.json")
    args = ap.parse_args()

    projects = Path(args.claude_dir).expanduser() / "projects"
    if not projects.is_dir():
        sys.exit(f"error: {projects} not found — is this a Claude Code machine?")

    files = sorted(projects.glob("*/*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    files = files[: args.sessions]
    if not files:
        sys.exit(f"error: no session transcripts under {projects}")

    sessions, project_dirs = [], {}
    total_user, total_hits = 0, 0
    all_first, all_last = None, None
    for p in files:
        hits, cwd, user_msgs, first_ts, last_ts = scan_session(p)
        total_user += user_msgs
        total_hits += len(hits)
        if first_ts and (all_first is None or first_ts < all_first):
            all_first = first_ts
        if last_ts and (all_last is None or last_ts > all_last):
            all_last = last_ts
        if cwd:
            project_dirs[cwd] = project_dirs.get(cwd, 0) + 1
        if hits:
            sessions.append({
                "session": p.stem,
                "project": cwd or p.parent.name,
                "mtime": p.stat().st_mtime,
                "hits": hits,
            })

    out = {
        "scanned_sessions": len(files),
        "date_range": {"from": all_first, "to": all_last},
        "total_user_messages": total_user,
        "total_correction_hits": total_hits,
        "project_dirs": sorted(project_dirs, key=project_dirs.get, reverse=True),
        "sessions": sessions,
    }
    Path(args.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"scanned {len(files)} sessions, {total_user} user messages, "
          f"{total_hits} correction hits -> {args.out}")


if __name__ == "__main__":
    main()
