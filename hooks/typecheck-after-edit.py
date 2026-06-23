#!/usr/bin/env python3
"""
PostToolUse hook: package-scoped type-check after edits.

Why this exists
---------------
The Stop hook (stop-verify-and-log.py) already type-checks, but it runs at the
*repo root* (the whole Turbo graph) AFTER Claude has stopped, and writes the
result to a log file + macOS notification. The errors never re-enter Claude's
context, so Claude can't self-correct from them during the turn — it declares
"done" and the breakage is found later.

This hook closes that gap. After each edit to a type-relevant file it:
  1. finds the *single nearest package* the file belongs to (not the whole repo),
  2. runs that package's own type-check (its `check` script, or `tsc --noEmit`),
  3. if it fails, prints the errors to stderr and exits 2 — which feeds the
     errors straight back into Claude's context so it fixes them immediately.

Speed
-----
A full type-check on every keystroke-edit would be unbearable in a monorepo, so:
  - it is scoped to one package (svelte-check on one package is seconds, not the
    90s a root `turbo check` takes),
  - it is debounced per-package: a burst of edits to the same package triggers
    at most one run per DEBOUNCE_SECONDS window. The Stop hook is the final
    backstop, so skipping intermediate runs is safe.

Tuning (env vars)
-----------------
  CLAUDE_SKIP_TYPECHECK=1   disable this hook entirely
  CLAUDE_TYPECHECK_DEBOUNCE seconds between runs per package (default 20)
  CLAUDE_TYPECHECK_TIMEOUT  max seconds for one check run (default 60)

Never crashes the turn: any unexpected error exits 0.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Extensions whose changes can introduce a type error worth catching now.
# Deliberately narrow — .json/.css/.md edits don't change types.
CHECK_EXTENSIONS = (".ts", ".tsx", ".svelte")

# Directories that mean "not source" — never walk into or check these.
SKIP_PATH_PARTS = (
    "node_modules", ".svelte-kit", "build", "dist", ".vercel",
    ".turbo", "__pycache__", ".git",
)

DEBOUNCE_SECONDS = int(os.environ.get("CLAUDE_TYPECHECK_DEBOUNCE", "20"))
TIMEOUT_SECONDS = int(os.environ.get("CLAUDE_TYPECHECK_TIMEOUT", "60"))

STATE_DIR = Path.home() / ".claude" / ".cache"
STATE_FILE = STATE_DIR / "typecheck-debounce.json"

# How many lines of diagnostics to surface. tsc/svelte-check print the most
# relevant errors first, then a "Found N errors" trailer — so we keep the HEAD.
MAX_LINES = 40


def in_skipped_path(path: Path) -> bool:
    return any(part in SKIP_PATH_PARTS for part in path.parts)


def find_package_dir(file_path: Path) -> Path | None:
    """Walk up from the edited file to the nearest dir holding a package.json.

    Stops at $HOME so we never escape into the user's home or above. Returns the
    package directory, or None if the file isn't inside a JS/TS package.
    """
    home = Path.home()
    for directory in file_path.parents:
        if (directory / "package.json").exists():
            return directory
        if directory == home or directory == directory.parent:
            break
    return None


def choose_command(pkg_dir: Path) -> tuple[list[str], str] | None:
    """Pick the cheapest faithful check for this package.

    Preference order:
      1. the package's own `check` script  → respects `svelte-kit sync`, the
         project's tsconfig, thresholds, etc. Scoped with `-C` so we run the
         *package* script, never the root `turbo check`.
      2. `tsc --noEmit` if a tsconfig exists but there is no check script.
    Returns (command, label) or None if there's nothing to run.
    """
    try:
        pkg = json.loads((pkg_dir / "package.json").read_text())
    except (json.JSONDecodeError, OSError):
        pkg = {}

    scripts = pkg.get("scripts", {})
    if isinstance(scripts, dict) and "check" in scripts:
        return ["pnpm", "-C", str(pkg_dir), "run", "check"], "check"

    if (pkg_dir / "tsconfig.json").exists():
        return ["pnpm", "-C", str(pkg_dir), "exec", "tsc", "--noEmit"], "tsc --noEmit"

    return None


def should_debounce(pkg_dir: str) -> bool:
    """True if we ran this package within the debounce window. Records now if not.

    Fails open: on any state-file error we run the check rather than skip it.
    """
    now = time.time()
    state: dict[str, float] = {}
    try:
        if STATE_FILE.exists():
            state = json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        state = {}

    last = state.get(pkg_dir, 0)
    if now - last < DEBOUNCE_SECONDS:
        return True

    state[pkg_dir] = now
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        # prune stale entries so the file can't grow without bound
        cutoff = now - 3600
        state = {k: v for k, v in state.items() if v >= cutoff}
        STATE_FILE.write_text(json.dumps(state))
    except OSError:
        pass
    return False


def main() -> None:
    if os.environ.get("CLAUDE_SKIP_TYPECHECK") == "1":
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    if data.get("tool_name", "") not in ("Edit", "MultiEdit", "Write"):
        sys.exit(0)

    # Only act on edits that actually succeeded.
    if not data.get("tool_response", {}).get("success", True):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    raw_path = tool_input.get("file_path") or tool_input.get("path") or ""
    if not raw_path:
        sys.exit(0)

    file_path = Path(raw_path)
    if file_path.suffix.lower() not in CHECK_EXTENSIONS:
        sys.exit(0)
    if in_skipped_path(file_path):
        sys.exit(0)

    pkg_dir = find_package_dir(file_path)
    if pkg_dir is None:
        sys.exit(0)

    command = choose_command(pkg_dir)
    if command is None:
        sys.exit(0)

    if should_debounce(str(pkg_dir)):
        sys.exit(0)

    cmd, label = command
    try:
        result = subprocess.run(
            cmd, cwd=pkg_dir,
            capture_output=True, text=True, timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        # Don't punish Claude for a slow check — the Stop hook will still run.
        sys.exit(0)
    except FileNotFoundError:
        # pnpm not on PATH in this context — nothing we can do, stay quiet.
        sys.exit(0)

    if result.returncode == 0:
        sys.exit(0)  # clean — say nothing

    # tsc / svelte-check write diagnostics to stdout; the pnpm wrapper to stderr.
    detail = (result.stdout or "").strip() or (result.stderr or "").strip()
    lines = detail.splitlines()
    head = "\n".join(lines[:MAX_LINES])
    more = f"\n… ({len(lines) - MAX_LINES} more lines)" if len(lines) > MAX_LINES else ""

    print(
        f"Type-check failed in package '{pkg_dir.name}' ({label}). "
        f"Fix these before continuing — do not declare the task done:\n\n"
        f"{head}{more}",
        file=sys.stderr,
    )
    sys.exit(2)  # exit 2 → stderr is fed back to Claude


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # A hook must never crash the turn.
        sys.exit(0)
