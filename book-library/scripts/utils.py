"""
Shared utilities for the book library CLI.

Provides:
- DB_PATH  : default SQLite database file location
- get_conn : open (and optionally create) the SQLite database
- print_books : render a list of book rows as a Rich table
- no_results  : print a friendly "nothing found" message
- logger   : pre-configured logger (level from BOOKLIBRARY_LOG_LEVEL)
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from pathlib import Path
from typing import Any, Sequence

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import box

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

load_dotenv(Path.home() / ".config" / "skills" / "book-library" / ".env")

# The database lives next to the project root by default, but can be
# overridden with the BOOKLIBRARY_DB environment variable.
_DEFAULT_DB = Path(__file__).resolve().parent.parent / "books.db"
DB_PATH = Path(os.environ.get("BOOKLIBRARY_DB", _DEFAULT_DB))

console = Console()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_LOG_FILE = Path.home() / "local" / "state" / "skills" / "booklibrary.log"
_LOG_LEVEL = os.environ.get("BOOKLIBRARY_LOG_LEVEL", "ERROR").upper()
 
_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=_LOG_LEVEL,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(_LOG_FILE, encoding="utf-8")],
)

logger = logging.getLogger("booklibrary")

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
    isbn            TEXT,
    date_added      TEXT
);

CREATE INDEX IF NOT EXISTS idx_author     ON books (author  COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_title      ON books (title   COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_isbn       ON books (isbn);
CREATE INDEX IF NOT EXISTS idx_year       ON books (year_published);
CREATE INDEX IF NOT EXISTS idx_date_added ON books (date_added);
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
        logger.error("Database not found: %s", path)
        console.print(
            f"[bold red]Database not found:[/] {path}\n"
            "Run [bold]books import <csv-file>[/] first to create it."
        )
        raise SystemExit(1)

    logger.debug("Opening database: %s", path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    if create:
        logger.debug("Initialising schema in: %s", path)
        conn.executescript(SCHEMA)
        conn.commit()

    _migrate(conn)

    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """Add columns introduced after the initial schema, if missing."""
    existing = {row[1] for row in conn.execute("PRAGMA table_info(books)")}
    if "date_added" not in existing:
        logger.debug("Migrating schema: adding date_added column")
        conn.execute("ALTER TABLE books ADD COLUMN date_added TEXT")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_date_added ON books (date_added)")
        conn.commit()


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

COLUMNS = [
    ("Title",      "title",          "cyan",  40),
    ("Author",     "author",         "green", 25),
    ("Publisher",  "publisher",      "dim",   22),
    ("Year",       "year_published", "dim",    6),
    ("ISBN",       "isbn",           "dim",   14),
    ("Date Added", "date_added",     "dim",   12),
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
            str(row["date_added"] or ""),
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


# ---------------------------------------------------------------------------
# JSON output helpers
# ---------------------------------------------------------------------------

def rows_to_dicts(rows: Sequence[sqlite3.Row]) -> list[dict]:
    """Convert a list of sqlite3.Row objects to plain dicts."""
    return [dict(row) for row in rows]


def output_json(data: Any) -> None:
    """Print data as formatted JSON to stdout."""
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
