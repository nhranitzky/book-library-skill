# Book Library Skill for Openclaw

An [Openclaw](https://openclaw.ai) skill that lets you search and browse your personal book collection from the terminal — or by asking your AI assistant. Backed by a local SQLite database populated from a CSV export.

> Built for readers who track their books in **BookBuddy** (or any app that exports CSV).

---

## How It Works

1. Export your book list as a CSV from BookBuddy (or any compatible app)
2. Import the CSV into a local SQLite database with `books import`
3. Install the skill in Openclaw — your AI can now search your library on your behalf

---

## Project Structure

```
book-library-skill/
├── Makefile                      ← Dev tasks: install, lint, package, deploy
├── install-skill.sh              ← Full deploy + remote install in one step
└── book-library/                 ← The Openclaw skill package
    ├── SKILL.md                  ← Skill manifest and AI instructions
    ├── pyproject.toml            ← Python dependencies (click, rich)
    ├── bin/
    │   └── books                 ← Shell launcher
    ├── scripts/
    │   ├── main.py               ← CLI entry point
    │   ├── utils.py              ← Shared DB helpers and Rich output
    │   ├── cmd_import.py         ← books import
    │   ├── cmd_search.py         ← books search
    │   ├── cmd_author.py         ← books author
    │   ├── cmd_title.py          ← books title
    │   ├── cmd_isbn.py           ← books isbn
    │   ├── cmd_year.py           ← books year
    │   ├── cmd_list.py           ← books list
    │   └── cmd_stats.py          ← books stats
    └── references/
        └── installation.md       ← Detailed installation guide
```

---

## Requirements

| Tool | Version |
|------|---------|
| [uv](https://docs.astral.sh/uv/) | ≥ 0.4 |
| Python | ≥ 3.11 (managed by uv) |

---

## Setup

**1. Install dependencies**

```bash
make install
```

**2. Set the database path**

```bash
export BOOKS_DB=/path/to/your/books.db
```

Add this to your shell profile (`~/.zshrc` or `~/.bashrc`) to make it permanent.

---

## Importing Your Book Collection

Export your books from **BookBuddy** as a CSV file, then import it:

```bash
books import ~/Downloads/my_books.csv
```

This creates the SQLite database on first run. The command is safe to re-run — books with a matching ISBN are skipped automatically.

```bash
# Full refresh (replace records with matching ISBN)
books import my_books.csv --replace

# Clean slate (wipe everything, then import)
books import my_books.csv --clear
```

### CSV Format

The importer expects a header row. BookBuddy's default export maps directly to the expected columns:

| Column | Required |
|--------|----------|
| `Title` | Yes |
| `Author` | |
| `Publisher` | |
| `Year Published` | |
| `Summary` | |
| `ISBN` | |

Extra columns are silently ignored.

---

## Available Commands

```bash
books search "machine learning"          # Keyword search across all fields
books author Tolkien                     # Search by author (partial match)
books title "Clean Code"                 # Search by title (partial match)
books isbn 978-0-13-235088-4            # Exact ISBN lookup
books year 2020 --to 2024               # Books by publication year range
books list --sort year --limit 30        # Browse all books
books stats                              # Library overview and top authors
```

All search commands support:
- `--summary / -s` — include the book summary in output
- `--limit N / -n N` — cap the number of results

---

## Installing the Skill in Openclaw

The skill is in the folder `book-library`.
 
To install manually on the Openclaw device:

- copy the `book-library` to the skill folder of Openclaw
- execute the `install-skill.sh` script

    ```bash
    cd ~/.openclaw/skills/book-library
    bash install-skill.sh
    ```

    The installer will:
    - Install Python dependencies with `uv sync`
    - Prompt for the SQLite database path
    - Register the skill via `openclaw config set` (sets the `BOOKS_DB` path in Openclaw's config)
 
- Check if the skill is ready:

```bash
openclaw skills info book-library
```

- create a new session in your messaging app

## License

MIT
