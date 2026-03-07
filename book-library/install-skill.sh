#!/bin/bash

# sync the virtual environment dependencies first
echo "Installing dependencies with uv sync..."
uv sync --no-dev
echo "Set execute permissions for bin/books..."
chmod +x bin/books

# prompt for sqlite database path and verify
read -p "Path to SQLite books database: " DB_PATH
if [ -f "$DB_PATH" ]; then
    echo "✓ database found at $DB_PATH"
else
    echo "⚠ Warning: database file not found at $DB_PATH"
    echo "  You can create it using 'books import'"
fi
echo "Configuring the skill in OpenClaw..." 
openclaw config set skills.entries."book-library".enabled true --json
openclaw config set skills.entries."book-library".env.BOOKS_DB "$DB_PATH" --json   
 