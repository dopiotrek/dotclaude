#!/usr/bin/env python3
"""
PreToolUse hook: Supabase RLS Reminder
Reminds to add Row Level Security policies when creating new tables.

Checks:
- New table definitions in Drizzle schema files
- Migration files creating tables without RLS
- Warns about tables that should have organizationId for multi-tenant isolation
"""

import json
import re
import sys
from pathlib import Path

# ANSI color codes for terminal formatting
class Colors:
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    # Colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    # Reset
    RESET = '\033[0m'

def styled(text: str, *styles: str) -> str:
    """Apply ANSI styles to text."""
    return ''.join(styles) + text + Colors.RESET

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "rls-reminder.log"

# Tables that typically need RLS for multi-tenant isolation
MULTI_TENANT_INDICATORS = [
    'organizationId',
    'organization_id',
    'profileId',
    'profile_id',
    'userId',
    'user_id',
    'accountId',
    'account_id',
]

# Tables that are typically public/shared (don't need tenant isolation)
PUBLIC_TABLES = [
    'service_categories',
    'company_types',
    'countries',
    'states',
    'cities',
    'industries',
    'skills',
    'certifications',
    'subscription_plans',
    'feature_flags',
    # Auth tables managed by Supabase
    'auth.users',
    'auth.sessions',
]

# Schema file patterns
SCHEMA_PATHS = ['schema/', 'packages/db/schema/']
MIGRATION_PATHS = ['migrations/', 'packages/db/migrations/']


def log(message: str) -> None:
    """Log to file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def is_schema_file(file_path: str) -> bool:
    """Check if file is a Drizzle schema file."""
    path = Path(file_path)
    return (
        path.suffix == '.ts' and
        any(sp in file_path for sp in SCHEMA_PATHS) and
        'index.ts' not in file_path
    )


def is_migration_file(file_path: str) -> bool:
    """Check if file is a migration file."""
    path = Path(file_path)
    return (
        path.suffix == '.sql' and
        any(mp in file_path for mp in MIGRATION_PATHS)
    )


def extract_table_name_from_schema(content: str) -> list[str]:
    """Extract table names from Drizzle schema definition."""
    tables = []
    # Match: export const tableName = pgTable('table_name', {
    pattern = r"export\s+const\s+(\w+)\s*=\s*pgTable\s*\(\s*['\"](\w+)['\"]"
    matches = re.findall(pattern, content)
    for var_name, table_name in matches:
        tables.append(table_name)
    return tables


def extract_table_name_from_migration(content: str) -> list[str]:
    """Extract table names from CREATE TABLE statements."""
    tables = []
    # Match: CREATE TABLE table_name or CREATE TABLE "table_name"
    pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["\']?(\w+)["\']?'
    matches = re.findall(pattern, content, re.IGNORECASE)
    tables.extend(matches)
    return tables


def check_has_tenant_column(content: str) -> bool:
    """Check if content has multi-tenant isolation columns."""
    return any(indicator in content for indicator in MULTI_TENANT_INDICATORS)


def check_has_rls_statement(content: str, table_name: str) -> bool:
    """Check if migration has RLS enabled for table."""
    # Check for ALTER TABLE ... ENABLE ROW LEVEL SECURITY
    rls_pattern = rf'ALTER\s+TABLE\s+["\']?{table_name}["\']?\s+ENABLE\s+ROW\s+LEVEL\s+SECURITY'
    return bool(re.search(rls_pattern, content, re.IGNORECASE))


def is_public_table(table_name: str) -> bool:
    """Check if table is typically public/shared."""
    return table_name in PUBLIC_TABLES or table_name.startswith('_')


def analyze_schema_file(content: str, file_path: str) -> dict:
    """Analyze Drizzle schema file for RLS considerations."""
    result = {
        'warnings': [],
        'info': [],
        'tables': []
    }

    tables = extract_table_name_from_schema(content)
    result['tables'] = tables

    for table in tables:
        if is_public_table(table):
            continue

        has_tenant_col = check_has_tenant_column(content)

        if has_tenant_col:
            result['info'].append(
                f"ℹ️  Table '{table}' has tenant column - ensure RLS policies exist in Supabase"
            )
        else:
            # Check if this might need tenant isolation
            if not any(pub in table for pub in ['type', 'category', 'status', 'config']):
                result['warnings'].append(
                    f"⚠️  Table '{table}' may need organizationId for multi-tenant isolation"
                )

    return result


def analyze_migration_file(content: str, file_path: str) -> dict:
    """Analyze migration file for RLS."""
    result = {
        'warnings': [],
        'info': [],
        'tables': []
    }

    tables = extract_table_name_from_migration(content)
    result['tables'] = tables

    for table in tables:
        if is_public_table(table):
            continue

        has_rls = check_has_rls_statement(content, table)
        has_tenant_col = check_has_tenant_column(content)

        if not has_rls and has_tenant_col:
            result['warnings'].append(
                f"⚠️  Table '{table}' has tenant column but no RLS enabled in this migration"
            )
            result['info'].append(
                f"   💡 Add: ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;"
            )
            result['info'].append(
                f"   💡 Then create policies for SELECT, INSERT, UPDATE, DELETE"
            )

        elif not has_rls and not has_tenant_col:
            # Only warn for tables that look like they need tenant isolation
            if any(keyword in table.lower() for keyword in ['user', 'account', 'profile', 'org', 'team', 'member', 'crm', 'deal', 'contact', 'invoice', 'proposal', 'mission', 'job', 'equipment', 'fleet']):
                result['warnings'].append(
                    f"⚠️  Table '{table}' may need RLS for data isolation"
                )

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

    result = None

    if is_schema_file(file_path):
        result = analyze_schema_file(content, file_path)
        log(f"Analyzing schema: {Path(file_path).name}")
    elif is_migration_file(file_path):
        result = analyze_migration_file(content, file_path)
        log(f"Analyzing migration: {Path(file_path).name}")
    else:
        sys.exit(0)

    # Log findings
    if result:
        for item in result['info']:
            log(f"  {item}")
        for item in result['warnings']:
            log(f"  {item}")

    # Only warn, never block (RLS is a reminder, not enforcement)
    if result and (result['warnings'] or result['info']):
        # Build structured JSON response with ANSI-formatted terminal output
        response = {
            "decision": "continue",
            "reason": "RLS reminder for database security"
        }

        # Terminal output with ANSI colors
        lines = []
        lines.append("")
        lines.append(styled("🔐 Supabase RLS Reminder", Colors.BOLD, Colors.CYAN))
        lines.append(styled("─" * 50, Colors.DIM))
        lines.append(f"   {styled('File:', Colors.BOLD)} {styled(Path(file_path).name, Colors.WHITE)}")

        if result['tables']:
            tables_str = ', '.join(styled(t, Colors.YELLOW) for t in result['tables'])
            lines.append(f"   {styled('Tables:', Colors.BOLD)} {tables_str}")

        if result['warnings']:
            lines.append("")
            lines.append(styled("   ⚠️  Warnings:", Colors.BOLD, Colors.YELLOW))
            for warning in result['warnings']:
                # Strip existing emoji and re-add with color
                clean_warning = warning.replace('⚠️', '').strip()
                lines.append(f"   {styled('•', Colors.YELLOW)} {clean_warning}")

        if result['info']:
            lines.append("")
            lines.append(styled("   ℹ️  Info:", Colors.BOLD, Colors.BLUE))
            for info in result['info']:
                clean_info = info.replace('ℹ️', '').replace('💡', '').strip()
                lines.append(f"   {styled('•', Colors.BLUE)} {clean_info}")

        if result['warnings']:
            lines.append("")
            lines.append(styled("   📚 Resources:", Colors.BOLD, Colors.MAGENTA))
            lines.append(f"   {styled('•', Colors.MAGENTA)} {styled('https://supabase.com/docs/guides/auth/row-level-security', Colors.UNDERLINE, Colors.CYAN)}")
            lines.append("")
            lines.append(styled("   💡 Common RLS pattern:", Colors.BOLD, Colors.GREEN))
            lines.append(styled("   ┌─────────────────────────────────────────────────", Colors.DIM))
            pipe = styled('│', Colors.DIM)
            lines.append(f"   {pipe} {styled('ALTER TABLE', Colors.MAGENTA)} table_name {styled('ENABLE ROW LEVEL SECURITY', Colors.MAGENTA)};")
            lines.append(f"   {pipe}")
            lines.append(f"   {pipe} {styled('CREATE POLICY', Colors.MAGENTA)} {styled('\"org_isolation\"', Colors.GREEN)} {styled('ON', Colors.MAGENTA)} table_name")
            org_id_str = styled("'organization_id'", Colors.GREEN)
            lines.append(f"   {pipe}   {styled('FOR ALL USING', Colors.MAGENTA)} (organization_id = auth.jwt() ->> {org_id_str});")
            lines.append(styled("   └─────────────────────────────────────────────────", Colors.DIM))

        lines.append("")

        response["message"] = "\n".join(lines)

        # Output JSON response
        print(json.dumps(response))
        log("RLS reminder issued (JSON response)")

    sys.exit(0)  # Always allow - this is just a reminder


if __name__ == "__main__":
    main()
