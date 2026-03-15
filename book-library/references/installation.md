# book-library Installation

Personal book library search tool for the terminal.
Import your book list from a CSV file, then search by author, title, ISBN,
or publication year – all from a fast local SQLite database.

---

## Requirements

| Tool | Version | Install |
|------|---------|---------|
| [uv](https://docs.astral.sh/uv/) | ≥ 0.4 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Python | ≥ 3.11 | managed automatically by `uv` |

> **Note:** `uv` downloads and manages Python automatically. You do not need
> a separate Python installation.

---

## Installation

### 1 – Get the project

```bash
git clone https://github.com/your-org/books-skill.git
cd books-skill
```

Or simply copy the `books-skill/` folder wherever you like.

### 2 – Install dependencies

```bash
uv sync
```

This creates a `.venv/` directory and installs `click` and `rich`
as declared in `pyproject.toml`. No other packages are needed
(SQLite is part of Python's standard library).

### 3 – Make the launcher executable

```bash
chmod +x bin/books
```
 

---

## Quick Start

### Step 1 – Prepare your CSV

Your CSV file must have a header row. Column names are case-insensitive.

```
Title,Author,Publisher,Year Published,Summary,ISBN
The Hobbit,J.R.R. Tolkien,Allen & Unwin,1937,A fantasy novel about...,978-0-261-10221-7
Clean Code,Robert C. Martin,Prentice Hall,2008,A handbook of agile...,978-0-13-235088-4
```

The `Title` column is the only required field. All others are optional.

### Step 2 – Import your book list

```bash
books import my_books.csv
```

This creates `books.db` in the project root and imports all rows.
The command is safe to re-run — books with a matching ISBN are skipped.

```bash
# Full refresh (replace records with matching ISBN)
books import my_books.csv --replace

# Clean slate (delete everything, then import)
books import my_books.csv --clear
```

### Step 3 – Search

```bash
# By author (partial match, case-insensitive)
books author Tolkien
books author "Ursula Le Guin" --summary

# By title
books title "Lord of the Rings"
books title clean code

# By ISBN (hyphens/spaces are stripped automatically)
books isbn 978-0-13-235088-4
books isbn 9780132350884

# By publication year
books year 1984
books year 1990 --to 1999

# Keyword search across all fields
books search "machine learning" python
books search dragon --summary

# Browse all books
books list
books list --sort year --limit 20
books list --sort author --offset 100

# Library statistics
books stats
books stats --top 20
```

---

## CSV Column Reference

| Column name | Accepted variants | Notes |
|-------------|-------------------|-------|
| `Title` | `title` | **Required** |
| `Author` | `author` | |
| `Publisher` | `publisher` | |
| `Year Published` | `year_published`, `year` | Integer year |
| `Summary` | `summary`, `description` | Free text |
| `ISBN` | `isbn` | ISBN-10 or ISBN-13 |

Extra columns in your CSV are silently ignored.

---

## Running Without Adding to PATH

From inside the project root:

```bash
uv run python -m scripts.main import my_books.csv
uv run python -m scripts.main search Tolkien
```

From anywhere, specifying the project:

```bash
uv run --project /path/to/books-skill python -m scripts.main stats
```

---

## Custom Database Location

By default the database is stored as `books.db` in the project root.
Override this with the `BOOKLIBRARY_DB` environment variable:

```bash
export BOOKLIBRARY_DB=/home/you/data/library.db
books import my_books.csv
books search Tolkien
```

---

## Project Structure

```
books-skill/
├── SKILL.md              ← Claude skill metadata & instructions
├── pyproject.toml        ← Python project / uv configuration
├── README.md             ← this file
├── books.db              ← SQLite database (created on first import)
├── bin/
│   └── books            ← shell launcher
└── scripts/
    ├── __init__.py
    ├── main.py           ← CLI entry point (Click)
    ├── utils.py          ← shared DB helpers and Rich formatting
    ├── cmd_import.py     ← `books import`
    ├── cmd_search.py     ← `books search`
    ├── cmd_author.py     ← `books author`
    ├── cmd_title.py      ← `books title`
    ├── cmd_isbn.py       ← `books isbn`
    ├── cmd_year.py       ← `books year`
    ├── cmd_list.py       ← `books list`
    └── cmd_stats.py      ← `books stats`
```

---
## Openclaw Configuration

The skip tge manual approval: add to `exec-approvals.json`

```json
"allowlist": [
        {
          "pattern": "**/book-library/bin/books",
        },
]
````


## Troubleshooting

| Problem | Solution |
|---------|----------|
| `command not found: books` | Check PATH, or run `./bin/books` from the project root |
| `Database not found` | Run `books import <file.csv>` first |
| `CSV is missing required column` | Ensure your CSV has a `Title` column (case-insensitive) |
| Empty results | Try a shorter / broader search term; check spelling |
| Wrong year results | Ensure `Year Published` contains plain integers in your CSV |

---



## Adding New Search Commands

1. Create `scripts/cmd_<name>.py` with a `@click.command()` function.
2. Import and register it in `scripts/main.py`.
3. Use `get_conn()` from `scripts/utils.py` for DB access.
4. Use `print_books()` for consistent output formatting.

## License

MIT
