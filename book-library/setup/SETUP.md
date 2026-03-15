# Book Library – Setup Guide

---

## Installation for Openclaw

### 1. Unzip the skill

Unzip `book-library.skill_v1.0.zip` into the Openclaw skills directory:

```bash
unzip book-library.skill_v1.0.zip -d ~/.openclaw/skills/
```

This creates `~/.openclaw/skills/book-library/`.

### 2. Run the setup script

```bash
cd ~/.openclaw/skills/book-library
bash setup/setup-openclaw.sh
```

The script will:
- Install Python dependencies with `uv sync --no-dev`
- Check for `BOOKLIBRARY_DB` in `~/.config/skills/book-library/.env`
- Prompt for the database path if not set (with the option to set it manually later)
- Register the skill and `BOOKLIBRARY_DB` in Openclaw via `openclaw config set`
- Add `bin/books` to the Openclaw exec-approvals allowlist

### 3. Verify the skill is active

```bash
openclaw skills info book-library
```

---

## Installation for Claude Code

### 1. Unzip the skill

Unzip `book-library.skill_v1.0.zip` into a directory of your choice:

```bash
unzip book-library.skill_v1.0.zip -d ~/skills/
```

This creates `~/skills/book-library/`.

### 2. Run the setup script

```bash
cd ~/skills/book-library
bash setup/setup-claude.sh
```

The script will:
- Install Python dependencies with `uv sync`
- Check for `BOOKLIBRARY_DB` in `~/.config/skills/book-library/.env`
- Prompt for the database path if not set

### 3. Verify the installation

```bash
bin/books --help
```

---

## Creating the Database

The SQLite database is created on first import from a CSV file.

### Export your books

Export your book list from **BookBuddy** (or any compatible app) as a CSV file. The importer expects a header row with these columns (case-insensitive, extra columns are ignored):

| Column | Required | Notes |
|--------|----------|-------|
| `Title` | Yes | |
| `Author` | | |
| `Publisher` | | |
| `Year Published` | | Integer year |
| `Summary` | | |
| `ISBN` | | ISBN-10 or ISBN-13 |
| `Date Added` | | Any common date format; stored as YYYY-MM-DD |

### Import the CSV

```bash
bin/books import ~/Downloads/my_books.csv
```

This creates the database at the path configured in `BOOKLIBRARY_DB`. The command is safe to re-run — books with a matching ISBN are skipped automatically.

```bash
# Replace records with matching ISBN
bin/books import my_books.csv --replace

# Wipe the database and import fresh
bin/books import my_books.csv --clear
```

### Verify the import

```bash
bin/books stats
```
