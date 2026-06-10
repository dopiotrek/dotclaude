#!/usr/bin/env python3
"""build_map.py — render a yoda topic map and run spaced-repetition scheduling.

Source of truth is state.json (see references/state-schema.md). This script never
asks the agent to do date math: `review` applies the SM-2-lite algorithm, `build`
regenerates the views, `due` lists what's owed.

Stdlib only. Python 3.8+.

    python build_map.py build  <state.json>
    python build_map.py review <state.json> --item c1 --grade ok [--date YYYY-MM-DD]
    python build_map.py due    <state.json> [--date YYYY-MM-DD]

As a convenience, `python build_map.py <state.json>` is treated as `build`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

EASE_DEFAULT = 2.3
EASE_FLOOR = 1.3
EASE_CAP = 3.0
TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "map_template.html"
STATUS_ORDER = {"learned": 0, "learning": 1, "locked": 2}


# ---------------------------------------------------------------- io helpers
def load(state_path: Path) -> dict:
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"error: no state file at {state_path}")
    except json.JSONDecodeError as e:
        sys.exit(f"error: {state_path} is not valid JSON ({e})")


def save(state_path: Path, state: dict) -> None:
    state["updated"] = today_iso()
    state_path.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def today_iso() -> str:
    return dt.date.today().isoformat()


def parse_date(s: str | None) -> dt.date:
    return dt.date.today() if not s else dt.date.fromisoformat(s)


# ---------------------------------------------------------- reviewable items
def reviewables(state: dict):
    """Yield (kind, item) for every chunk and grammar."""
    for c in state.get("chunks", []):
        yield "chunk", c
    for g in state.get("grammars", []):
        yield "grammar", g


def find_item(state: dict, item_id: str):
    for kind, item in reviewables(state):
        if item.get("id") == item_id:
            return kind, item
    return None, None


def label_for(kind: str, item: dict) -> str:
    if kind == "grammar":
        return f"grammar of {item.get('region', '?')}"
    return item.get("title", item.get("id", "?"))


# --------------------------------------------------------- the scheduler
def apply_grade(item: dict, grade: str, today: dt.date) -> None:
    """Mutate item['reviews'] per SM-2-lite. See references/state-schema.md."""
    r = item.setdefault(
        "reviews", {"ease": EASE_DEFAULT, "interval": 0, "reps": 0, "history": []}
    )
    ease = float(r.get("ease", EASE_DEFAULT))
    interval = int(r.get("interval", 0))
    reps = int(r.get("reps", 0))

    if grade == "hard":
        reps = 0
        interval = 1
        ease = max(EASE_FLOOR, ease - 0.20)
    elif grade == "ok":
        reps += 1
        interval = 1 if reps == 1 else 4 if reps == 2 else round(interval * ease)
    elif grade == "easy":
        reps += 1
        interval = 2 if reps == 1 else 6 if reps == 2 else round(interval * (ease + 0.15))
        ease = min(EASE_CAP, ease + 0.10)
    else:
        sys.exit(f"error: grade must be easy|ok|hard, got {grade!r}")

    interval = max(1, interval)
    r["ease"] = round(ease, 3)
    r["interval"] = interval
    r["reps"] = reps
    r["last_review"] = today.isoformat()
    r["next_due"] = (today + dt.timedelta(days=interval)).isoformat()
    r.setdefault("history", []).append({"date": today.isoformat(), "grade": grade})
    item["reviews"] = r
    item["status"] = "learned"
    item.setdefault("learned_on", today.isoformat())


def due_items(state: dict, on: dt.date):
    out = []
    for kind, item in reviewables(state):
        nd = item.get("reviews", {}).get("next_due")
        if nd and dt.date.fromisoformat(nd) <= on:
            out.append((kind, item, nd))
    out.sort(key=lambda t: t[2])
    return out


# ----------------------------------------------------------------- stats
def stats(state: dict) -> dict:
    chunks = state.get("chunks", [])
    learned = sum(1 for c in chunks if c.get("status") == "learned")
    total = len(chunks)
    today = dt.date.today()
    due = len(due_items(state, today))
    started = [int(c["mastery"]) for c in chunks
               if isinstance(c.get("mastery"), (int, float)) and c["mastery"] > 0]
    level = round(sum(started) / len(started), 1) if started else 0
    return {
        "learned": learned,
        "total": total,
        "pct": round(100 * learned / total) if total else 0,
        "due": due,
        "level": level,
        "regions": len(state.get("terrain", {}).get("regions", [])),
        "grammars": len(state.get("grammars", [])),
    }


# ------------------------------------------------------------- rendering
def render_html(state: dict) -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    # Escape </ so the JSON can't terminate the <script> element early.
    blob = json.dumps(state, ensure_ascii=False).replace("</", "<\\/")
    return template.replace("__STATE_JSON__", blob)


def render_md(state: dict) -> str:
    s = stats(state)
    regions = state.get("terrain", {}).get("regions", [])
    here = state.get("you_are_here")
    by_region = {}
    for c in state.get("chunks", []):
        by_region.setdefault(c.get("region", "?"), []).append(c)

    L = []
    L.append(f"# {state.get('topic', 'Untitled topic')}")
    L.append("")
    if state.get("one_sentence"):
        L.append(f"> {state['one_sentence']}")
        L.append("")
    meta = []
    if state.get("goal"):
        meta.append(f"**Goal:** {state['goal']}")
    if state.get("level"):
        meta.append(f"**Starting point:** {state['level']}")
    if meta:
        L.append("  ·  ".join(meta))
        L.append("")
    mlabels = state.get("mastery_labels") or ["Unseen", "Fragile", "Working", "Solid", "Expert"]
    lvl = s["level"]
    lbl = mlabels[int(round(lvl))] if (mlabels and lvl) else "—"
    L.append(
        f"**Progress:** {s['learned']}/{s['total']} chunks ({s['pct']}%)  ·  "
        f"overall level **{lvl}** ({lbl})  ·  {s['grammars']} grammar(s)  ·  {s['due']} due"
    )
    L.append("")
    L.append("_Generated from state.json — do not edit by hand._")
    L.append("")

    # Terrain
    L.append("## The terrain")
    L.append("")
    for r in regions:
        flag = "★" if r.get("core") else "·"
        tier = r.get("tier")
        tierlbl = f" _[{tier}]_" if tier else ""
        youhere = "  ← you are here" if r.get("id") == here else ""
        L.append(f"- {flag} **{r.get('title','?')}**{tierlbl} — {r.get('summary','')}{youhere}")
        for mm in (r.get("models") or []):
            L.append(f"    - _model:_ **{mm.get('name','?')}** — {mm.get('note','')}")
    notc = state.get("terrain", {}).get("not_covered", [])
    if notc:
        L.append("")
        L.append(f"_Out of scope: {', '.join(notc)}._")
    L.append("")

    # The path — chunks by region, with mastery
    L.append("## The path")
    L.append("")
    for r in regions:
        rid = r.get("id")
        items = by_region.get(rid, [])
        if not items:
            continue
        L.append(f"### {r.get('title','?')}")
        L.append("")
        for c in items:
            box = {"learned": "[x]", "learning": "[~]"}.get(c.get("status"), "[ ]")
            m = c.get("mastery")
            mstr = f" · L{int(m)}" if isinstance(m, (int, float)) else ""
            nd = c.get("reviews", {}).get("next_due")
            duestr = f" _(review {nd})_" if nd else ""
            L.append(f"- {box} **{c.get('title','?')}**{mstr}{duestr}")
            if c.get("note"):
                L.append(f"  - {c['note']}")
            if c.get("gap"):
                L.append(f"  - _gap →_ {c['gap']}")
            for mm in (c.get("models") or []):
                L.append(f"  - _model:_ **{mm.get('name','?')}** — {mm.get('note','')}")
            sch = c.get("schema")
            if sch and sch.get("nodes"):
                sep = " ↓ " if sch.get("type") == "stack" else " → "
                L.append(f"  - _schema:_ {sep.join(sch['nodes'])}")
            if c.get("recall_q"):
                L.append(f"  - ❓ {c['recall_q']}")
        L.append("")

    # Grammars
    grammars = state.get("grammars", [])
    if grammars:
        L.append("## The grammar")
        L.append("")
        for g in grammars:
            vrs = ", ".join(g.get("variables", []))
            L.append(f"### {g.get('region','?')} — _{vrs}_")
            L.append("")
            L.append(g.get("paragraph", ""))
            L.append("")

    # Open questions
    oq = [q for q in state.get("open_questions", []) if not q.get("resolved")]
    if oq:
        L.append("## Parked questions")
        L.append("")
        for q in oq:
            L.append(f"- {q.get('text','?')}")
        L.append("")

    return "\n".join(L).rstrip() + "\n"


def build(state_path: Path, state: dict) -> None:
    (state_path.parent / "map.html").write_text(render_html(state), encoding="utf-8")
    (state_path.parent / "map.md").write_text(render_md(state), encoding="utf-8")


# ------------------------------------------------------------------- cli
def cmd_build(args):
    p = Path(args.state)
    state = load(p)
    build(p, state)
    s = stats(state)
    print(f"built {p.parent/'map.html'} and map.md — "
          f"{s['learned']}/{s['total']} chunks ({s['pct']}%), {s['due']} due")


def cmd_review(args):
    p = Path(args.state)
    state = load(p)
    kind, item = find_item(state, args.item)
    if not item:
        sys.exit(f"error: no chunk or grammar with id {args.item!r}")
    apply_grade(item, args.grade, parse_date(args.date))
    save(p, state)
    build(p, state)
    r = item["reviews"]
    print(f"reviewed {args.item} ({label_for(kind, item)}): "
          f"grade={args.grade} → next due {r['next_due']} "
          f"(interval {r['interval']}d, ease {r['ease']})")


def cmd_due(args):
    p = Path(args.state)
    state = load(p)
    on = parse_date(args.date)
    items = due_items(state, on)
    if not items:
        print(f"nothing due on or before {on.isoformat()} — you're clear.")
        return
    print(f"{len(items)} item(s) due on or before {on.isoformat()}:")
    for kind, item, nd in items:
        last = (item.get("reviews", {}).get("history") or [{}])[-1].get("grade", "—")
        print(f"  · [{nd}] {item.get('id'):>4}  {label_for(kind, item)}  (last: {last})")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # convenience: `build_map.py foo/state.json` == `build_map.py build foo/state.json`
    if argv and argv[0].endswith(".json"):
        argv = ["build"] + argv

    parser = argparse.ArgumentParser(description="Render a yoda topic map and schedule reviews.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="regenerate map.html + map.md")
    b.add_argument("state")
    b.set_defaults(func=cmd_build)

    r = sub.add_parser("review", help="apply a review grade to one item")
    r.add_argument("state")
    r.add_argument("--item", required=True, help="chunk or grammar id, e.g. c1 / g1")
    r.add_argument("--grade", required=True, choices=["easy", "ok", "hard"])
    r.add_argument("--date", help="override today (YYYY-MM-DD)")
    r.set_defaults(func=cmd_review)

    d = sub.add_parser("due", help="list items due on/before a date")
    d.add_argument("state")
    d.add_argument("--date", help="override today (YYYY-MM-DD)")
    d.set_defaults(func=cmd_due)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
