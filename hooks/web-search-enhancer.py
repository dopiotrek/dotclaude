#!/usr/bin/env python3
"""
PreToolUse hook: Enhance WebSearch queries with current year.
Adds the current year to queries that lack temporal context to get fresher results.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "web-search.log"

# Words that indicate the query already has temporal context
TEMPORAL_KEYWORDS = [
    'latest', 'recent', 'current', 'new', 'now', 'today',
    '2024', '2025', '2026',  # Explicit years
    'yesterday', 'this week', 'this month', 'this year',
    'updated', 'newest', 'modern',
]

# Topics that benefit from year context
TECH_KEYWORDS = [
    'documentation', 'docs', 'api', 'tutorial', 'guide',
    'best practices', 'how to', 'example', 'setup',
    'install', 'configuration', 'release', 'version',
    'framework', 'library', 'package', 'npm', 'pip',
]


def log(message: str) -> None:
    """Log to file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")


def has_year(query: str) -> bool:
    """Check if query already contains a year (2020-2029)."""
    return bool(re.search(r'\b20[2-3]\d\b', query))


def has_temporal_context(query: str) -> bool:
    """Check if query has words indicating temporal context."""
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in TEMPORAL_KEYWORDS)


def is_tech_query(query: str) -> bool:
    """Check if query is likely tech-related and would benefit from year."""
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in TECH_KEYWORDS)


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    if tool_name != "WebSearch":
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    query = tool_input.get("query", "")

    if not query:
        sys.exit(0)

    current_year = str(datetime.now().year)

    # Decide whether to add year
    should_add_year = (
        not has_year(query) and
        not has_temporal_context(query) and
        is_tech_query(query)  # Only add year for tech queries
    )

    if should_add_year:
        modified_query = f"{query} {current_year}"
        log(f"Enhanced: '{query}' → '{modified_query}'")

        # Output modified query for Claude Code to use
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "modifiedToolInput": {
                    "query": modified_query
                }
            }
        }
        print(json.dumps(output))
    else:
        log(f"Unchanged: '{query}'")

    sys.exit(0)


if __name__ == "__main__":
    main()
