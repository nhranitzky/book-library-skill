#!/bin/bash
set -euo pipefail

# Resolve the skill root (one level up from this script's directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Setting up book-library skill..."
echo "Skill root: $SKILL_ROOT"

# Install dependencies
echo ""
echo "Installing dependencies with uv sync..."
uv sync --no-dev --project "$SKILL_ROOT"

# Make the launcher executable
echo "Setting execute permissions for bin/books..."
chmod +x "$SKILL_ROOT/bin/books"

# Read DB_PATH from ~/.config/skills/book-library/.env
ENV_FILE="$HOME/.config/skills/book-library/.env"
DB_PATH=""

if [ -f "$ENV_FILE" ]; then
    DB_PATH="$(grep -E '^BOOKS_DB=' "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")"
fi

if [ -z "$DB_PATH" ]; then
    echo ""
    echo "BOOKS_DB not set in $ENV_FILE"
    read -p "Set the database path now? [y/N] " SET_NOW
    if [[ "$SET_NOW" =~ ^[Yy]$ ]]; then
        read -p "Path to SQLite books database: " DB_PATH
        mkdir -p "$(dirname "$ENV_FILE")"
        echo "BOOKS_DB=$DB_PATH" >> "$ENV_FILE"
        echo "  Saved to $ENV_FILE"
    else
        echo ""
        echo "  You can set BOOKS_DB later in one of two ways:"
        echo "    1. Add it to $ENV_FILE:"
        echo "         BOOKS_DB=/path/to/books.db"
        echo "    2. Set it in the Openclaw configuration:"
        echo "         openclaw config set skills.entries.\"book-library\".env.BOOKS_DB /path/to/books.db --json"
    fi
fi

if [ -n "$DB_PATH" ]; then
    if [ -f "$DB_PATH" ]; then
        echo "  database found at $DB_PATH"
    else
        echo "  Warning: database file not found at $DB_PATH"
        echo "  You can create it by running: books import <file.csv>"
    fi
fi

# Register the skill with Openclaw
echo ""
echo "Configuring the skill in Openclaw..."
openclaw config set skills.entries."book-library".enabled true --json
if [ -n "$DB_PATH" ]; then
    openclaw config set skills.entries."book-library".env.BOOKS_DB "$DB_PATH" --json
fi

# Add bin/books to exec-approvals allowlist
echo "Adding bin/books to Openclaw exec-approvals allowlist..."
openclaw config set exec-approvals.allowlist '{"pattern":"**/book-library/bin/books"}' 2>/dev/null || \
    echo "  Note: could not update exec-approvals automatically. Add manually if needed:"  && \
    echo '  { "pattern": "**/book-library/bin/books" }'

echo ""
echo "Setup complete. Test with: $SKILL_ROOT/bin/books --help"
