#!/usr/bin/env python3
"""
PostToolUse hook: Monitor bundle size and performance for SvelteKit builds.
Triggers on: pnpm build, vite build, turbo build commands
Checks: .svelte-kit/output bundle sizes, code patterns that affect performance
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Configuration
BUNDLE_BUDGET_KB = 1000  # Total JS bundle budget in KB
CHUNK_BUDGET_KB = 100   # Individual chunk budget in KB
FILE_SIZE_WARN_KB = 100 # Warn if single source file exceeds this
MAX_IMPORTS_WARN = 15   # Warn if file has more than this many imports

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "sveltekit-perf.log"

# Patterns that may affect bundle size negatively
PERF_ANTIPATTERNS = [
    (r"import\s+\*\s+as\s+\w+\s+from", "Wildcard import detected - use named imports for better tree-shaking"),
    (r"from\s+['\"]lodash['\"]", "Full lodash import - use 'lodash-es' or specific imports like 'lodash-es/debounce'"),
    (r"from\s+['\"]moment['\"]", "Moment.js detected - consider date-fns or native Intl API for smaller bundle"),
    (r"from\s+['\"]@tabler/icons-svelte['\"](?!\s*;)", "Importing from barrel - prefer '@tabler/icons-svelte/icons/IconName'"),
]

# SvelteKit-specific patterns to check
SVELTE_PATTERNS = [
    (r"(?<!export\s)const\s+\w+\s*=\s*\$state\([^)]*\)\s*;?\s*$", "Top-level $state outside component may cause issues"),
    (r"onMount\([^)]*fetch\(", "Consider using +page.server.ts load function instead of onMount fetch"),
]


def log(message: str) -> None:
    """Log to both stdout and file."""
    print(message)
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")


def get_dir_size(path: Path) -> int:
    """Get total size of all files in directory recursively."""
    total = 0
    if path.exists():
        for file in path.rglob("*"):
            if file.is_file():
                total += file.stat().st_size
    return total


def get_js_files_sizes(path: Path) -> list[tuple[Path, int]]:
    """Get list of JS files with their sizes, sorted by size descending."""
    files = []
    if path.exists():
        for file in path.rglob("*.js"):
            if file.is_file():
                files.append((file, file.stat().st_size))
    return sorted(files, key=lambda x: x[1], reverse=True)


def find_sveltekit_output() -> Path | None:
    """Find SvelteKit build output directory."""
    # Check common locations
    candidates = [
        Path(".svelte-kit/output/client/_app/immutable"),
        Path(".svelte-kit/output/client"),
        Path("build/client/_app/immutable"),
        Path("build/client"),
        Path(".vercel/output/static/_app/immutable"),
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def analyze_build() -> bool:
    """Analyze SvelteKit build output for bundle size."""
    output_dir = find_sveltekit_output()

    if not output_dir:
        log("❌ No SvelteKit build output found. Run build first.")
        return True  # Don't block, just warn

    log(f"\n📊 Performance Budget Guard: Analyzing {output_dir}...")

    # Get JS bundle sizes
    js_files = get_js_files_sizes(output_dir)
    total_js_size = sum(size for _, size in js_files)
    total_js_kb = total_js_size // 1024

    log(f"\n📦 Total JS bundle size: {total_js_kb}KB")

    budget_exceeded = False

    # Check total budget
    if total_js_kb > BUNDLE_BUDGET_KB:
        budget_exceeded = True
        overage = total_js_kb - BUNDLE_BUDGET_KB
        log(f"\n🚨 PERFORMANCE BUDGET EXCEEDED!")
        log(f"   Current: {total_js_kb}KB")
        log(f"   Budget:  {BUNDLE_BUDGET_KB}KB")
        log(f"   Overage: {overage}KB")
    else:
        remaining = BUNDLE_BUDGET_KB - total_js_kb
        log(f"✅ Bundle within budget: {total_js_kb}KB / {BUNDLE_BUDGET_KB}KB")
        log(f"🎯 Remaining budget: {remaining}KB")

        if remaining < 50:
            log(f"⚠️  Warning: Less than 50KB remaining in budget")

    # Show largest chunks
    log(f"\n📋 Largest chunks:")
    for file, size in js_files[:5]:
        size_kb = size // 1024
        marker = "🚨" if size_kb > CHUNK_BUDGET_KB else "  "
        log(f"   {marker} {size_kb:>4}KB  {file.name}")

    # Check for large individual chunks
    large_chunks = [(f, s) for f, s in js_files if s // 1024 > CHUNK_BUDGET_KB]
    if large_chunks:
        log(f"\n⚠️  {len(large_chunks)} chunk(s) exceed {CHUNK_BUDGET_KB}KB limit")
        log("💡 Consider code splitting with dynamic imports")

    if budget_exceeded:
        log("\n💡 Optimization recommendations:")
        log("   • Use dynamic imports: const Component = await import('./heavy.svelte')")
        log("   • Lazy load routes with +page.ts export const prerender = false")
        log("   • Check for duplicate dependencies: pnpm why <package>")
        log("   • Analyze bundle: npx vite-bundle-visualizer")
        log("   • Remove unused dependencies")

    return not budget_exceeded


def analyze_file(file_path: str) -> None:
    """Analyze a single source file for performance issues."""
    path = Path(file_path)

    if not path.exists():
        return

    # Only check JS/TS/Svelte files
    if path.suffix not in ('.js', '.jsx', '.ts', '.tsx', '.svelte'):
        return

    # Skip node_modules and build output
    if 'node_modules' in str(path) or '.svelte-kit' in str(path):
        return

    log(f"\n🔍 Performance check: {path.name}")

    file_size = path.stat().st_size
    file_size_kb = file_size // 1024

    if file_size_kb > FILE_SIZE_WARN_KB:
        log(f"⚠️  Large file: {file_size_kb}KB")
        log("💡 Consider splitting into smaller components")

    content = path.read_text(errors='ignore')

    # Count imports
    imports = re.findall(r'^import\s+', content, re.MULTILINE)
    if len(imports) > MAX_IMPORTS_WARN:
        log(f"📦 Many imports: {len(imports)} imports")
        log("💡 Consider consolidating or lazy loading")

    # Check for anti-patterns
    issues_found = False
    for pattern, message in PERF_ANTIPATTERNS + SVELTE_PATTERNS:
        if re.search(pattern, content):
            if not issues_found:
                log("\n⚠️  Performance issues found:")
                issues_found = True
            log(f"   • {message}")

    if not issues_found and file_size_kb <= FILE_SIZE_WARN_KB:
        log("✅ No performance issues detected")


def is_build_command(command: str) -> bool:
    """Check if command is a build command."""
    build_patterns = [
        r'pnpm\s+(run\s+)?build',
        r'npm\s+run\s+build',
        r'yarn\s+build',
        r'turbo\s+(run\s+)?build',
        r'vite\s+build',
        r'svelte-kit\s+build',
    ]
    return any(re.search(p, command) for p in build_patterns)


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    tool_response = input_data.get("tool_response", {})

    # Check if operation was successful
    # For Bash, check exit code or success field
    success = tool_response.get("success", True)
    if isinstance(tool_response, dict) and "exitCode" in tool_response:
        success = tool_response.get("exitCode", 0) == 0

    if not success:
        sys.exit(0)  # Skip analysis for failed operations

    # Handle Bash commands (build detection)
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if is_build_command(command):
            log("\n" + "=" * 60)
            log("🏗️  SvelteKit Build Completed - Running Performance Analysis")
            log("=" * 60)

            if not analyze_build():
                # Budget exceeded - exit with error to show warning
                log("\n" + "=" * 60)
                sys.exit(2)

            log("\n" + "=" * 60)

    # Handle file edits
    elif tool_name in ("Write", "Edit", "MultiEdit"):
        file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
        if file_path:
            analyze_file(file_path)

    sys.exit(0)


if __name__ == "__main__":
    main()
