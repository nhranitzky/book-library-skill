---
name: book-library
description: Search and manage a personal book list stored in a local SQLite database, imported from a CSV file . Use this skill whenever the user wants to search their book collection by author, title, ISBN, or publication year; browse all books; get statistics
user-invocable: true
licence: MIT
metadata: { "openclaw": {"emoji": "📚" } }
---

# Book Library Skill

Search a personal book collection backed by **SQLite**, populated from a CSV
file. All scripts live in `scripts/`, managed with `uv`, launched via `bin/books`.


## Available Commands

Prepend the full path of the launcher script: `{baseDir}/bin/books <action> [options]`

| Command | User asks |
|---------|-------------|
| `{baseDir}/bin/books import <file.csv>` | Load CSV into SQLite (idempotent, skips duplicates by ISBN) |
| `{baseDir}/bin/books import <file.csv> --replace` | Replace records sharing an ISBN |
| `{baseDir}/bin/books import <file.csv> --clear` | Wipe the table, then import fresh |
| `{baseDir}/bin/books search <query…>` | Keyword search across title, author, publisher, summary |
| `{baseDir}/bin/books author <name…>` | Search by author (partial, case-insensitive) |
| `{baseDir}/bin/books title <title…>` | Search by title (partial, case-insensitive) |
| `{baseDir}/bin/books isbn <isbn>` | Exact ISBN lookup (hyphens/spaces stripped automatically) |
| `{baseDir}/bin/books year <year>` | All books published in a specific year |
| `{baseDir}/bin/books year <year> --to <year>` | Books published within a year range |
| `{baseDir}/bin/books list` | Browse all books (paginated, sortable) |
| `{baseDir}/bin/books stats` | Library overview: counts, top authors, publishers, decades |

 
## Key Options (all search commands)

- `--summary / -s` — include the summary column in output
- `--limit N / -n N` — cap result rows (default varies per command)
 


## CSV Format

The import command expects a CSV file with a **header row** using these column names
(case-insensitive, extra columns are ignored):

| Column | Required | Notes |
|--------|----------|-------|
| `Title` | ✅ | Book title |
| `Author` | | Author name(s) |
| `Publisher` | | Publisher name |
| `Year Published` | | Integer year, e.g. `1984` |
| `Summary` | | Free-text description |
| `ISBN` | | ISBN-10 or ISBN-13, hyphens optional |


## How Openclaw Should Use This Skill

1. **Identify intent** — import CSV / search / browse / statistics.
2. **Extract parameters** from the user's message (author name, title fragment, ISBN, year).
3. **Run the appropriate command** via `{baseDir}/bin/books`  
4. **Relay results** — summarise the table or highlight the best match.

## Example Invocations

```bash
# First-time setup
{baseDir}/bin/books import ~/Downloads/my_books.csv

# Search
{baseDir}/bin/books search "artificial intelligence"
{baseDir}/bin/books author "Tolkien" --summary
{baseDir}/bin/books title "Clean Code"
{baseDir}/bin/books isbn 978-0-13-235088-4
{baseDir}/bin/books year 2020 --to 2024

# Browse & stats
{baseDir}/bin/books list --sort year --limit 30
{baseDir}/bin/books stats --top 15

```

