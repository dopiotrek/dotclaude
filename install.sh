#!/bin/bash
# install.sh - Install Claude Code configuration via symlinks
#
# This script creates symlinks from your ~/.claude directory to this repository,
# making this repo the single source of truth for your Claude Code configuration.
#
# Usage:
#   ./install.sh           # Install with symlinks
#   ./install.sh --copy    # Install by copying (no symlinks)
#   ./install.sh --uninstall  # Remove symlinks and restore backup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$CLAUDE_DIR/backup-$(date +%Y%m%d-%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}        ${GREEN}dotclaude${NC} - Claude Code Configuration Framework       ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}▸${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

print_error() {
    echo -e "${RED}✖${NC}  $1"
}

print_success() {
    echo -e "${GREEN}✔${NC}  $1"
}

# Handle uninstall
if [[ "$1" == "--uninstall" ]]; then
    print_header
    echo "Uninstalling dotclaude configuration..."
    echo ""

    # Find most recent backup
    LATEST_BACKUP=$(ls -td "$CLAUDE_DIR"/backup-* 2>/dev/null | head -1)

    # Remove symlinks
    for item in CLAUDE.md hooks agents skills; do
        if [ -L "$CLAUDE_DIR/$item" ]; then
            rm "$CLAUDE_DIR/$item"
            print_success "Removed symlink: $item"
        fi
    done

    # Restore from backup if exists
    if [ -n "$LATEST_BACKUP" ] && [ -d "$LATEST_BACKUP" ]; then
        echo ""
        read -p "Restore from backup ($LATEST_BACKUP)? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for item in CLAUDE.md hooks agents skills; do
                if [ -e "$LATEST_BACKUP/$item" ]; then
                    cp -r "$LATEST_BACKUP/$item" "$CLAUDE_DIR/"
                    print_success "Restored: $item"
                fi
            done
        fi
    fi

    echo ""
    print_success "Uninstall complete!"
    exit 0
fi

print_header

# Check if Claude CLI is installed
if ! command -v claude &> /dev/null; then
    print_warning "Claude CLI not found. Install from: https://claude.ai/download"
    echo "         The configuration will still be installed."
    echo ""
fi

# 1. Create ~/.claude if it doesn't exist
if [ ! -d "$CLAUDE_DIR" ]; then
    print_step "Creating ~/.claude directory..."
    mkdir -p "$CLAUDE_DIR"
fi

# 2. Backup existing config (only real files, not symlinks)
has_existing=false
for item in CLAUDE.md settings.json hooks agents skills; do
    if [ -e "$CLAUDE_DIR/$item" ] && [ ! -L "$CLAUDE_DIR/$item" ]; then
        has_existing=true
        break
    fi
done

if [ "$has_existing" = true ]; then
    print_step "Backing up existing config to $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    for item in CLAUDE.md settings.json hooks agents skills; do
        if [ -e "$CLAUDE_DIR/$item" ] && [ ! -L "$CLAUDE_DIR/$item" ]; then
            cp -r "$CLAUDE_DIR/$item" "$BACKUP_DIR/" 2>/dev/null || true
            print_success "Backed up: $item"
        fi
    done
    echo ""
fi

# 3. Create symlinks or copy files
if [[ "$1" == "--copy" ]]; then
    print_step "Installing via copy (no symlinks)..."

    cp "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
    cp -r "$SCRIPT_DIR/hooks" "$CLAUDE_DIR/hooks"
    cp -r "$SCRIPT_DIR/agents" "$CLAUDE_DIR/agents"
    cp -r "$SCRIPT_DIR/skills" "$CLAUDE_DIR/skills"
else
    print_step "Creating symlinks..."

    # CLAUDE.md
    rm -f "$CLAUDE_DIR/CLAUDE.md"
    ln -s "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
    print_success "CLAUDE.md → $SCRIPT_DIR/CLAUDE.md"

    # Hooks directory
    rm -rf "$CLAUDE_DIR/hooks"
    ln -s "$SCRIPT_DIR/hooks" "$CLAUDE_DIR/hooks"
    print_success "hooks/    → $SCRIPT_DIR/hooks/"

    # Agents directory
    rm -rf "$CLAUDE_DIR/agents"
    ln -s "$SCRIPT_DIR/agents" "$CLAUDE_DIR/agents"
    print_success "agents/   → $SCRIPT_DIR/agents/"

    # Skills directory
    rm -rf "$CLAUDE_DIR/skills"
    ln -s "$SCRIPT_DIR/skills" "$CLAUDE_DIR/skills"
    print_success "skills/   → $SCRIPT_DIR/skills/"
fi

echo ""

# 4. Generate settings.json from template
print_step "Generating settings.json..."
if [ -f "$SCRIPT_DIR/settings/settings.template.json" ]; then
    # Replace $HOME with actual home directory
    sed "s|\\\$HOME|$HOME|g" "$SCRIPT_DIR/settings/settings.template.json" > "$CLAUDE_DIR/settings.json"
    print_success "settings.json generated with your \$HOME path"
else
    print_warning "settings.template.json not found, skipping settings generation"
fi

# 5. Ensure hook scripts are executable
print_step "Setting hook permissions..."
chmod +x "$SCRIPT_DIR/hooks/"*.py 2>/dev/null || true
print_success "Hook scripts marked as executable"

# 6. Create logs directory
mkdir -p "$CLAUDE_DIR/logs"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ Installation complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Installed components:"
echo "  • CLAUDE.md    - Global preferences and instructions"
echo "  • 13 hooks     - Automated guardrails and enhancements"
echo "  • 9 agents     - Specialized task handlers"
echo "  • 4 skills     - Reusable skill definitions"
echo "  • settings.json - Permissions and hook configuration"
echo ""

if [[ "$1" != "--copy" ]]; then
    echo -e "${BLUE}ℹ${NC}  Symlink mode: Edit files in this repo to update your config"
    echo "   Repository: $SCRIPT_DIR"
fi

echo ""
echo "Next steps:"
echo "  1. Start a new Claude Code session to use the new config"
echo "  2. Customize CLAUDE.md with your preferences"
echo "  3. Review and customize hooks for your workflow"
echo ""
