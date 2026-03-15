# Book Library Skill

Search and browse your personal book collection from the terminal. Backed by a local SQLite database populated from a CSV export.

> Built for readers who track their books in **BookBuddy** (or any app that exports CSV).

---

## Installation

See [setup/SETUP.md](book-library/setup/SETUP.md) for installation instructions — both for **Openclaw** and **Claude Code**.

---

## Project Structure

```
book-library-skill/
├── Makefile                      ← Dev tasks: install, lint, package, deploy
└── book-library/                 ← The skill package
    ├── SKILL.md                  ← Skill manifest and AI instructions
    ├── pyproject.toml            ← Python dependencies
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
    │   ├── cmd_added_date.py     ← books added-date
    │   ├── cmd_list.py           ← books list
    │   └── cmd_stats.py          ← books stats
    └── setup/
        ├── SETUP.md              ← Installation guide
        ├── setup-openclaw.sh     ← Openclaw setup script
        └── setup-claude.sh       ← Claude Code setup script
```

---

## Creating the Database

Export your books from **BookBuddy** as a CSV file, then import it:

```bash
books import ~/Downloads/my_books.csv
```

This creates the SQLite database on first run. The command is safe to re-run — books with a matching ISBN are skipped automatically.

```bash
books import my_books.csv --replace   # Replace records with matching ISBN
books import my_books.csv --clear     # Wipe everything, then import fresh
```

### CSV Format

The importer expects a header row. BookBuddy's default export maps directly to these columns (case-insensitive, extra columns are ignored):

| Column | Required | Notes |
|--------|----------|-------|
| `Title` | Yes | |
| `Author` | | |
| `Publisher` | | |
| `Year Published` | | Integer year |
| `Summary` | | |
| `ISBN` | | ISBN-10 or ISBN-13 |
| `Date Added` | | Any common date format; stored as YYYY-MM-DD |

---

## CLI Reference

```bash
books import <file.csv>                        # Import books from CSV
books search <query...>                        # Keyword search across all fields
books author <name...>                         # Search by author (partial match)
books title <title...>                         # Search by title (partial match)
books isbn <isbn>                              # Exact ISBN lookup
books year <year> [--to <year>]                # Books by publication year or range
books added-date [--from DATE] [--to DATE]     # Books by date added (interval)
books list [--sort FIELD] [--offset N]         # Browse all books
books stats                                    # Library overview and top authors
```

All search/list/stats commands support:

- `--summary` / `-s` — include the book summary in output
- `--limit N` / `-n N` — cap the number of results
- `--json` — output results as JSON instead of a table

### JSON output

`--json` outputs to stdout and is suitable for piping or AI consumption:

```bash
books author Tolkien --json
books stats --json
books list --json | jq '.[0]'
```

Book commands return a JSON array of objects with fields:
`id`, `title`, `author`, `publisher`, `year_published`, `summary`, `isbn`, `date_added`.

`books list --json` returns `{"total": N, "offset": N, "books": [...]}`.

`books stats --json` returns a stats object with `total`, `unique_authors`, `unique_publishers`, `year_min`, `year_max`, `missing_isbn`, `top_authors`, `top_publishers`, `top_decades`.

### `added-date` interval rules

| `--from` | `--to` | Result |
|----------|--------|--------|
| provided | provided | books added between the two dates (inclusive) |
| provided | omitted | books added from that date up to today |
| omitted | provided | all books added up to that date |
| omitted | omitted | all books that have a date added |

Dates are accepted in any common format (`YYYY-MM-DD`, `DD.MM.YYYY`, `DD/MM/YYYY`, `Month DD, YYYY`, etc.).

### Examples

```bash
books search "machine learning"
books author Tolkien --summary
books author Tolkien --json
books title "Clean Code"
books isbn 978-0-13-235088-4
books year 2020 --to 2024
books year 2020 --to 2024 --json
books added-date --from 2024-01-01
books added-date --from 2024-01-01 --to 2024-12-31
books added-date --to 2023-12-31
books list --sort year --limit 30
books list --json
books stats --top 15
books stats --json
```

---
## Development Notes

Parts of this codebase were generated or assisted by Claude Code Sonnet 4.6.
All generated code has been reviewed and tested by human developers.

## License

MIT
