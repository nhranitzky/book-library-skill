#!/bin/bash
set -euo pipefail

# Resolve the skill root (one level up from this script's directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Setting up book-library skill for Claude Code..."
echo "Skill root: $SKILL_ROOT"

# Install dependencies
echo ""
echo "Installing dependencies with uv sync..."
uv sync --project "$SKILL_ROOT"

# Make the launcher executable
echo "Setting execute permissions for bin/books..."
chmod +x "$SKILL_ROOT/bin/books"

# Check BOOKS_DB in ~/.config/skills/book-library/.env
ENV_FILE="$HOME/.config/skills/book-library/.env"
DB_PATH=""

if [ -f "$ENV_FILE" ]; then
    DB_PATH="$(grep -E '^BOOKS_DB=' "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")"
fi

if [ -n "$DB_PATH" ]; then
    echo ""
    echo "BOOKS_DB=$DB_PATH (from $ENV_FILE)"
    if [ -f "$DB_PATH" ]; then
        echo "  database found at $DB_PATH"
    else
        echo "  Warning: database file not found at $DB_PATH"
        echo "  Create it with: $SKILL_ROOT/bin/books import <file.csv>"
    fi
else
    echo ""
    echo "BOOKS_DB not set in $ENV_FILE"
    read -p "Path to SQLite books database: " DB_PATH
    mkdir -p "$(dirname "$ENV_FILE")"
    echo "BOOKS_DB=$DB_PATH" >> "$ENV_FILE"
    echo "  Saved to $ENV_FILE"
fi

echo ""
echo "Setup complete. Test with: $SKILL_ROOT/bin/books --help"
