#!/usr/bin/env python3
"""
PreToolUse hook: SvelteKit Route Validator
Enforces SvelteKit routing conventions and file structure.

Rules:
- Route files must follow +page.svelte, +page.server.ts conventions
- Warn about potential conflicts (+page.ts vs +page.server.ts)
- Validate route parameter syntax [param], [[optional]], [...rest]
- Check for common mistakes in route organization
"""

import json
import re
import sys
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "route-validator.log"

# Valid SvelteKit route file names
VALID_ROUTE_FILES = {
    '+page.svelte',
    '+page.ts',
    '+page.server.ts',
    '+layout.svelte',
    '+layout.ts',
    '+layout.server.ts',
    '+error.svelte',
    '+server.ts',
    '+server.js',
}

# Patterns for route directories
ROUTE_DIR_PATTERNS = [
    'src/routes/',
    'apps/web/src/routes/',
    'apps/marketing/src/routes/',
]

# Common mistakes to catch
ROUTE_MISTAKES = [
    # Wrong file names (missing + prefix)
    (r'/routes/.*/page\.svelte$', 'error', '🚨 Missing + prefix: should be +page.svelte'),
    (r'/routes/.*/layout\.svelte$', 'error', '🚨 Missing + prefix: should be +layout.svelte'),
    (r'/routes/.*/server\.ts$', 'error', '🚨 Missing + prefix: should be +server.ts'),
    (r'/routes/.*/error\.svelte$', 'error', '🚨 Missing + prefix: should be +error.svelte'),

    # Svelte 3 patterns (deprecated)
    (r'/routes/.*__layout\.svelte$', 'error', '🚨 __layout.svelte is Svelte 3 syntax. Use +layout.svelte'),
    (r'/routes/.*__error\.svelte$', 'error', '🚨 __error.svelte is Svelte 3 syntax. Use +error.svelte'),
    (r'/routes/.*/index\.svelte$', 'error', '🚨 index.svelte is outdated. Use +page.svelte'),

    # Common typos
    (r'/routes/.*\+pages\.svelte$', 'error', '🚨 Typo: +pages.svelte should be +page.svelte'),
    (r'/routes/.*\+layouts\.svelte$', 'error', '🚨 Typo: +layouts.svelte should be +layout.svelte'),
    (r'/routes/.*\+page\.server\.js$', 'warn', '⚠️  Using .js extension. Consider .ts for type safety'),

    # API route issues
    (r'/routes/api/.*\+page\.svelte$', 'warn', '⚠️  +page.svelte in api/ route. API routes typically use +server.ts only'),
]

# Content patterns to check
CONTENT_PATTERNS = [
    # Load function issues
    (
        r'export\s+const\s+load\s*=',
        r'\+page\.svelte$',
        'error',
        '🚨 load function in +page.svelte. Move to +page.ts or +page.server.ts'
    ),
    (
        r'export\s+const\s+actions\s*=',
        r'\+page\.svelte$',
        'error',
        '🚨 actions in +page.svelte. Move to +page.server.ts'
    ),
    (
        r'export\s+const\s+actions\s*=',
        r'\+page\.ts$',
        'error',
        '🚨 actions in +page.ts. Move to +page.server.ts (actions must be server-only)'
    ),

    # Deprecated patterns
    (
        r'import\s+.*\s+from\s+[\'\"]\$app/stores[\'\"]',
        r'\.svelte$',
        'warn',
        '⚠️  $app/stores is deprecated in Svelte 5. Use $app/state or props'
    ),

    # Server-only imports in client files
    (
        r'import\s+.*\s+from\s+[\'\"]\$env/static/private[\'\"]',
        r'\+page\.svelte$',
        'error',
        '🚨 Private env import in +page.svelte. Use +page.server.ts for server secrets'
    ),
    (
        r'import\s+.*\s+from\s+[\'\"]@dronelist/db[\'\"]',
        r'\+page\.svelte$',
        'error',
        '🚨 Database import in +page.svelte. Use +page.server.ts for DB queries'
    ),
]


def log(message: str) -> None:
    """Log to file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def is_route_file(file_path: str) -> bool:
    """Check if file is in a SvelteKit routes directory."""
    return any(pattern in file_path for pattern in ROUTE_DIR_PATTERNS)


def validate_route_path(file_path: str) -> tuple[list, list]:
    """Validate route file path for common mistakes."""
    errors = []
    warnings = []

    for pattern, level, message in ROUTE_MISTAKES:
        if re.search(pattern, file_path):
            if level == 'error':
                errors.append(message)
            else:
                warnings.append(message)

    # Check route parameter syntax
    path = Path(file_path)
    for part in path.parts:
        # Check for malformed parameters
        if '[' in part or ']' in part:
            # Valid: [param], [[optional]], [...rest]
            if not re.match(r'^(\[{1,2}\.{0,3}\w+\]{1,2}|\(\w+\)|[\w\-\.]+)$', part):
                if part.count('[') != part.count(']'):
                    errors.append(f'🚨 Malformed route parameter: {part} (mismatched brackets)')
                elif '[ ' in part or ' ]' in part:
                    errors.append(f'🚨 Spaces in route parameter: {part}')

    return errors, warnings


def validate_route_content(file_path: str, content: str) -> tuple[list, list]:
    """Validate route file content."""
    errors = []
    warnings = []

    for content_pattern, file_pattern, level, message in CONTENT_PATTERNS:
        if re.search(file_pattern, file_path) and re.search(content_pattern, content, re.MULTILINE):
            if level == 'error':
                errors.append(message)
            else:
                warnings.append(message)

    return errors, warnings


def check_file_naming(file_path: str) -> tuple[list, list]:
    """Check if route file follows naming conventions."""
    errors = []
    warnings = []

    path = Path(file_path)
    filename = path.name

    # Only check files in routes directory
    if not is_route_file(file_path):
        return errors, warnings

    # Check if it's a + prefixed file but not in valid list
    if filename.startswith('+') and filename not in VALID_ROUTE_FILES:
        # Allow variations like +page.svelte.test.ts
        if not any(filename.startswith(vf.replace('.', '')) for vf in VALID_ROUTE_FILES):
            warnings.append(f'⚠️  Unusual route file: {filename}. Expected one of: {", ".join(sorted(VALID_ROUTE_FILES))}')

    return errors, warnings


def analyze_route(file_path: str, content: str) -> dict:
    """Analyze a route file."""
    result = {
        'errors': [],
        'warnings': [],
        'is_route': False
    }

    if not is_route_file(file_path):
        return result

    result['is_route'] = True

    # Path validation
    path_errors, path_warnings = validate_route_path(file_path)
    result['errors'].extend(path_errors)
    result['warnings'].extend(path_warnings)

    # Naming validation
    name_errors, name_warnings = check_file_naming(file_path)
    result['errors'].extend(name_errors)
    result['warnings'].extend(name_warnings)

    # Content validation
    content_errors, content_warnings = validate_route_content(file_path, content)
    result['errors'].extend(content_errors)
    result['warnings'].extend(content_warnings)

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

    if not file_path:
        sys.exit(0)

    # Skip if not in routes directory
    if not is_route_file(file_path):
        sys.exit(0)

    # Analyze the route
    result = analyze_route(file_path, content)

    # Log analysis
    if result['is_route']:
        log(f"Analyzing route: {Path(file_path).name}")
        for item in result['warnings']:
            log(f"  {item}")
        for item in result['errors']:
            log(f"  {item}")

    # Block if there are errors
    if result['errors']:
        output = []
        output.append(f"\n🚨 SvelteKit Route Validator: Issues detected!")
        output.append(f"   File: {file_path}")
        output.append("")

        for error in result['errors']:
            output.append(f"   {error}")

        if result['warnings']:
            output.append("")
            output.append("   Additional warnings:")
            for warning in result['warnings']:
                output.append(f"   {warning}")

        output.append("")
        output.append("   💡 SvelteKit conventions:")
        output.append("   • Use +page.svelte for page components")
        output.append("   • Use +page.server.ts for server-side load/actions")
        output.append("   • Use +layout.svelte for shared layouts")
        output.append("   • Use +server.ts for API endpoints")
        output.append("")

        print("\n".join(output), file=sys.stderr)
        sys.exit(2)

    # Warn but allow if there are only warnings
    if result['warnings']:
        output = []
        output.append(f"\n⚠️  SvelteKit Route Validator: Suggestions")
        output.append(f"   File: {Path(file_path).name}")
        output.append("")

        for warning in result['warnings']:
            output.append(f"   {warning}")

        output.append("")

        print("\n".join(output), file=sys.stderr)
        log("Warnings issued but allowing operation")

    sys.exit(0)


if __name__ == "__main__":
    main()
