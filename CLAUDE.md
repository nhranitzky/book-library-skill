# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tech Stack

- Python 3.11+, managed with `uv`
- `click` for CLI, `rich` for terminal output
- SQLite for storage (no ORM)
- Makefile for development tasks

## Commands

```bash
make install    # Install dependencies (runs uv sync inside book-library/)
make lint       # Run ruff on book-library/scripts/
make package    # Zip the skill into book-library.skill_v1.0.zip
make clean      # Remove build artifacts, __pycache__, .venv, uv.lock
make deploy     # scp the zip and books.db to pi@openclaw.local
```

Set the database path before running:
```bash
export BOOKS_DB=$HOME/Projects/openclaw/skills/development/book-library-skill/data/books.db
```

Run the CLI directly during development:
```bash
book-library/bin/books <command> [options]
```

## Architecture

This is an **Openclaw skill** — a self-contained package that gets zipped and deployed to a device. The workspace has two layers:

- **Root** (`pyproject.toml`) — uv workspace wrapper; contains only the `book-library` member.
- **`book-library/`** — the actual skill package, described by `SKILL.md` for the Openclaw runtime.

### `book-library/` layout

| Path | Purpose |
|------|---------|
| `bin/books` | Bash launcher; resolves project root and calls `uv run python -m scripts.main` |
| `scripts/main.py` | Click group entry point; registers all subcommands |
| `scripts/utils.py` | Shared DB connection (`get_conn`), Rich table renderer (`print_books`), `DB_PATH` resolution |
| `scripts/cmd_*.py` | One file per subcommand (`import`, `search`, `author`, `title`, `isbn`, `year`, `list`, `stats`) |
| `SKILL.md` | Openclaw skill manifest (YAML front-matter + usage docs for the AI runtime) |
| `references/installation.md` | Install instructions |

### Database

SQLite file at `data/books.db` (outside the skill package). Path resolved via `BOOKS_DB` env var, falling back to `books.db` in the skill root. Schema is created on first `import` (`create=True` in `get_conn`). Indexes on `author`, `title`, `isbn`, `year_published`.

### Adding a new subcommand

1. Create `scripts/cmd_<name>.py` with a `@click.command()` function.
2. Import and register it in `scripts/main.py` via `cli.add_command(...)`.
3. Use `get_conn()` and `print_books()` from `utils.py` for DB access and output.
