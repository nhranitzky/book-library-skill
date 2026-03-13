"""
Shared utilities for the book library CLI.

Provides:
- DB_PATH  : default SQLite database file location
- get_conn : open (and optionally create) the SQLite database
- print_books : render a list of book rows as a Rich table
- no_results  : print a friendly "nothing found" message
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import box

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

load_dotenv(Path.home() / ".config" / "skills" / "book-library" / ".env")

# The database lives next to the project root by default, but can be
# overridden with the BOOKS_DB environment variable.
_DEFAULT_DB = Path(__file__).resolve().parent.parent / "books.db"
DB_PATH = Path(os.environ.get("BOOKS_DB", _DEFAULT_DB))

console = Console()

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT    NOT NULL,
    author          TEXT,
    publisher       TEXT,
    year_published  INTEGER,
    summary         TEXT,
    isbn            TEXT
);

CREATE INDEX IF NOT EXISTS idx_author  ON books (author  COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_title   ON books (title   COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_isbn    ON books (isbn);
CREATE INDEX IF NOT EXISTS idx_year    ON books (year_published);
"""


def get_conn(db_path: Path | None = None, *, create: bool = False) -> sqlite3.Connection:
    """
    Open a connection to the SQLite book database.

    Parameters
    ----------
    db_path : Path | None
        Override the default database path.
    create : bool
        If True, initialise the schema when the database does not yet exist.
        If False (default) and the database is missing, exit with an error.

    Returns
    -------
    sqlite3.Connection
        A configured connection with row_factory set to sqlite3.Row.
    """
    path = db_path or DB_PATH
    if not create and not path.exists():
        console.print(
            f"[bold red]Database not found:[/] {path}\n"
            "Run [bold]books import <csv-file>[/] first to create it."
        )
        raise SystemExit(1)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    if create:
        conn.executescript(SCHEMA)
        conn.commit()

    return conn


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

COLUMNS = [
    ("Title",     "title",          "cyan",  40),
    ("Author",    "author",         "green", 25),
    ("Publisher", "publisher",      "dim",   22),
    ("Year",      "year_published", "dim",    6),
    ("ISBN",      "isbn",           "dim",   14),
]


def print_books(rows: Sequence[sqlite3.Row], *, show_summary: bool = False) -> None:
    """
    Render book rows as a Rich table.

    Parameters
    ----------
    rows : sequence of sqlite3.Row
        Query results – must contain the standard book columns.
    show_summary : bool
        If True, append a "Summary" column (can be wide).
    """
    if not rows:
        no_results()
        return

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan",
                  show_lines=show_summary)

    for label, _field, style, width in COLUMNS:
        table.add_column(label, style=style, max_width=width, no_wrap=not show_summary)

    if show_summary:
        table.add_column("Summary", max_width=60, overflow="fold")

    for row in rows:
        cells = [
            str(row["title"] or ""),
            str(row["author"] or ""),
            str(row["publisher"] or ""),
            str(row["year_published"] or ""),
            str(row["isbn"] or ""),
        ]
        if show_summary:
            cells.append(str(row["summary"] or ""))
        table.add_row(*cells)

    console.print()
    console.print(table)
    console.print(f"  [dim]{len(rows)} book(s) found[/]")
    console.print()


def no_results(message: str = "No matching books found.") -> None:
    console.print(f"\n[yellow]{message}[/]\n")
