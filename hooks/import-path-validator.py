#!/usr/bin/env python3
"""
PreToolUse hook: Import Path Validator
Enforces import path conventions for the dronelist monorepo.

Rules:
- Use $lib alias instead of relative paths in SvelteKit apps
- Use @dronelist/* package imports for cross-package dependencies
- Never use relative paths across package boundaries
- Prefer named imports over barrel imports for tree-shaking
"""

import json
import re
import sys
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "import-validator.log"

# Patterns to check
IMPORT_PATTERNS = [
    # Cross-package relative imports (bad)
    (
        r'from\s+[\'"]\.\.\/\.\.\/\.\.\/packages\/',
        'error',
        '🚨 Cross-package relative import detected. Use @dronelist/* package imports instead.'
    ),
    (
        r'from\s+[\'"]\.\.\/\.\.\/\.\.\/apps\/',
        'error',
        '🚨 Cross-app relative import detected. Use package imports instead.'
    ),

    # Deep relative imports in SvelteKit (should use $lib)
    (
        r'from\s+[\'"]\.\.\/\.\.\/\.\.\/lib\/',
        'warn',
        '⚠️  Deep relative import to lib/. Consider using $lib alias.'
    ),
    (
        r'from\s+[\'"]\.\.\/.+\/\.\.\/.+\/',
        'warn',
        '⚠️  Complex relative path detected. Consider using $lib alias for clarity.'
    ),

    # Importing from node_modules with relative path (very bad)
    (
        r'from\s+[\'"]\.+\/node_modules\/',
        'error',
        '🚨 Relative import from node_modules. Import packages directly by name.'
    ),

    # Barrel import warnings (tree-shaking issues)
    (
        r'import\s+\*\s+as\s+\w+\s+from\s+[\'"](?!\@tabler)',
        'info',
        'ℹ️  Wildcard import may prevent tree-shaking. Prefer named imports.'
    ),

    # Common mistakes
    (
        r'from\s+[\'"]src\/lib\/',
        'error',
        '🚨 Absolute path from src/. Use $lib alias instead.'
    ),
    (
        r'from\s+[\'"]\/src\/',
        'error',
        '🚨 Absolute path starting with /src/. Use $lib or relative imports.'
    ),

    # Deprecated lucide-svelte (project uses tabler)
    (
        r'from\s+[\'"]lucide-svelte',
        'warn',
        '⚠️  lucide-svelte detected. This project uses @tabler/icons-svelte.'
    ),

    # Svelte 4 store import (deprecated in Svelte 5)
    (
        r'from\s+[\'\"]\$app\/stores[\'"]',
        'warn',
        '⚠️  $app/stores is deprecated in Svelte 5. Use $app/state instead.'
    ),
]

# Files to check
RELEVANT_EXTENSIONS = {'.ts', '.js', '.svelte', '.tsx', '.jsx'}

# Paths that indicate SvelteKit app context
SVELTEKIT_PATHS = ['apps/web/', 'apps/marketing/']


def log(message: str) -> None:
    """Log to file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def is_relevant_file(file_path: str) -> bool:
    """Check if file should be validated."""
    path = Path(file_path)
    return path.suffix in RELEVANT_EXTENSIONS


def is_sveltekit_context(file_path: str) -> bool:
    """Check if file is in a SvelteKit app."""
    return any(sp in file_path for sp in SVELTEKIT_PATHS)


def check_imports(content: str, file_path: str) -> tuple[list, list, list]:
    """Check content for import pattern violations."""
    errors = []
    warnings = []
    info = []

    is_svelte = is_sveltekit_context(file_path)

    for pattern, level, message in IMPORT_PATTERNS:
        matches = re.findall(pattern, content, re.MULTILINE)
        if matches:
            # Add context about which import triggered it
            for match in matches[:3]:  # Limit to first 3 matches
                context_msg = f"{message}"

                if level == 'error':
                    errors.append(context_msg)
                elif level == 'warn':
                    warnings.append(context_msg)
                else:
                    info.append(context_msg)

            # Only report once per pattern type
            break

    # Additional SvelteKit-specific checks
    if is_svelte:
        # Check for relative imports that could use $lib
        relative_to_lib = re.findall(
            r'from\s+[\'"](\.\.[\/\.].*?)[\'"]',
            content
        )
        deep_relatives = [r for r in relative_to_lib if r.count('..') >= 3]
        if deep_relatives and not any('$lib' in e for e in errors + warnings):
            warnings.append(
                f'⚠️  Found {len(deep_relatives)} deep relative import(s). '
                f'Consider using $lib alias for maintainability.'
            )

    return errors, warnings, info


def analyze_file(file_path: str, content: str) -> dict:
    """Analyze a file for import violations."""
    result = {
        'errors': [],
        'warnings': [],
        'info': [],
        'file_type': None
    }

    if not is_relevant_file(file_path):
        return result

    result['file_type'] = Path(file_path).suffix
    errors, warnings, info = check_imports(content, file_path)
    result['errors'].extend(errors)
    result['warnings'].extend(warnings)
    result['info'].extend(info)

    return result


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only check Write and Edit operations
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    content = tool_input.get("content", "") or tool_input.get("new_string", "")

    if not file_path or not content:
        sys.exit(0)

    # Skip if not a relevant file
    if not is_relevant_file(file_path):
        sys.exit(0)

    # Analyze the content
    result = analyze_file(file_path, content)

    # Log analysis
    if result['file_type']:
        log(f"Analyzing imports: {Path(file_path).name}")

        for item in result['info']:
            log(f"  {item}")
        for item in result['warnings']:
            log(f"  {item}")
        for item in result['errors']:
            log(f"  {item}")

    # Block if there are errors
    if result['errors']:
        output = []
        output.append(f"\n🚨 Import Path Validator: Invalid imports detected!")
        output.append(f"   File: {Path(file_path).name}")
        output.append("")

        for error in result['errors']:
            output.append(f"   {error}")

        if result['warnings']:
            output.append("")
            output.append("   Additional warnings:")
            for warning in result['warnings']:
                output.append(f"   {warning}")

        output.append("")
        output.append("   💡 Import conventions:")
        output.append("   • Use $lib/ for internal imports in SvelteKit apps")
        output.append("   • Use @dronelist/* for cross-package imports")
        output.append("   • Use package names directly for node_modules")
        output.append("")

        print("\n".join(output), file=sys.stderr)
        sys.exit(2)

    # Warn but allow if there are only warnings
    if result['warnings']:
        output = []
        output.append(f"\n⚠️  Import Path Validator: Suggestions")
        output.append(f"   File: {Path(file_path).name}")
        output.append("")

        for warning in result['warnings']:
            output.append(f"   {warning}")

        output.append("")

        # Print to stderr but don't block
        print("\n".join(output), file=sys.stderr)
        log("Warnings issued but allowing operation")

    sys.exit(0)


if __name__ == "__main__":
    main()
