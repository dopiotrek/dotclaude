#!/usr/bin/env python3
"""
PostToolUse hook: Run security audits when dependency files are modified.
Triggers on: package.json, pnpm-lock.yaml, requirements.txt, Cargo.toml, Gemfile

Registered with `async` in settings.json: the audit is a network call (0.6-2.3s
measured 2026-10-02) and never blocks, so the edit should not wait for it.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEPENDENCY_FILES = {
    "package.json": {"name": "pnpm", "command": ["pnpm", "audit", "--json"]},
    "pnpm-lock.yaml": {"name": "pnpm", "command": ["pnpm", "audit", "--json"]},
    "requirements.txt": {"name": "pip", "command": ["safety", "check", "-r"]},  # file path appended
    "Cargo.toml": {"name": "cargo", "command": ["cargo", "audit"]},
    "Gemfile": {"name": "bundler", "command": ["bundle", "audit", "check", "--update"]},
}

# The full advisory table is hundreds of lines in a monorepo. Only the tail
# (the totals) is worth the context.
MAX_LINES = 12


def resolve(tool: str, cwd: Path) -> str | None:
    """Find the tool even when it isn't on the PATH this hook inherits.

    mise only activates in interactive shells, so a pnpm installed under a
    mise-managed node is invisible here and the audit was skipped silently.
    """
    found = shutil.which(tool)
    if found or tool != "pnpm":
        return found

    mise = shutil.which("mise") or str(Path.home() / ".local" / "bin" / "mise")
    try:
        result = subprocess.run(
            [mise, "which", "pnpm"], cwd=cwd, capture_output=True, text=True, timeout=5
        )
        candidate = result.stdout.strip()
        if result.returncode == 0 and candidate and Path(candidate).exists():
            return candidate
    except (subprocess.TimeoutExpired, OSError):
        pass

    installs = Path.home() / ".local" / "share" / "mise" / "installs" / "node"
    candidates = sorted(installs.glob("*/bin/pnpm"))
    return str(candidates[-1]) if candidates else None


def pnpm_summary(stdout: str) -> str | None:
    try:
        counts = json.loads(stdout)["metadata"]["vulnerabilities"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return None
    found = {level: n for level, n in counts.items() if n}
    if not found:
        return "✅ No vulnerabilities found"
    parts = ", ".join(f"{n} {level}" for level, n in found.items())
    return f"⚠️  pnpm audit: {parts}. Run `pnpm audit` for details."


def run_audit(file_path: str) -> None:
    path = Path(file_path)
    config = DEPENDENCY_FILES[path.name]
    cmd = list(config["command"])
    if cmd[0] == "safety":
        cmd.append(file_path)

    tool = resolve(cmd[0], path.parent)
    if tool is None:
        print(f"⚠️  {cmd[0]} not found, skipping dependency audit of {file_path}")
        return

    # pnpm's launcher runs `node` from PATH; put its own bin dir first.
    env = {**os.environ, "PATH": f"{Path(tool).parent}{os.pathsep}{os.environ.get('PATH', '')}"}
    try:
        result = subprocess.run(
            [tool, *cmd[1:]], capture_output=True, text=True,
            cwd=path.parent, env=env, timeout=60,
        )
    except subprocess.TimeoutExpired:
        print(f"⚠️  {cmd[0]} audit timed out")
        return
    except OSError as e:
        print(f"⚠️  Error running {cmd[0]}: {e}")
        return

    print(f"📦 Dependency file modified: {file_path}")
    summary = pnpm_summary(result.stdout) if config["name"] == "pnpm" else None
    if summary:
        print(summary)
        return

    lines = ((result.stdout or "") + (result.stderr or "")).strip().splitlines()
    print("\n".join(lines[-MAX_LINES:]))
    if result.returncode != 0:
        print(f"⚠️  Audit found issues (exit code {result.returncode})")
    else:
        print("✅ No vulnerabilities found")


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    if input_data.get("tool_name", "") not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")

    if file_path and Path(file_path).name in DEPENDENCY_FILES:
        run_audit(file_path)

    # PostToolUse hooks should not block, always exit 0
    sys.exit(0)


if __name__ == "__main__":
    main()
