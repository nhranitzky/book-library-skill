"""
books import – Load a CSV book list into the SQLite database.

CSV format (with header row):
    Title,Author,Publisher,Year Published,Summary,ISBN

The command is idempotent:
  - Without flags        : skips books whose ISBN already exists (safe re-run).
  - With --replace       : replaces every existing record (full refresh).
  - With --clear         : wipes the table before importing (clean slate).

The database file is created automatically on first run.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import click
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from scripts.utils import console, DB_PATH, get_conn


def _normalise_year(raw: str) -> int | None:
    """Parse a year string; return None for blanks or non-numeric values."""
    s = raw.strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def _read_csv(path: Path) -> list[dict]:
    """
    Read the CSV file and return a list of normalised row dicts.

    Expected header (case-insensitive):
        Title, Author, Publisher, Year Published, Summary, ISBN
    """
    rows: list[dict] = []
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)

        # Normalise header names: strip whitespace, lower-case for lookup
        if reader.fieldnames is None:
            console.print("[red]CSV file appears to be empty.[/]")
            sys.exit(1)

        # Build a mapping from normalised key → original key
        norm = {k.strip().lower().replace(" ", "_"): k for k in reader.fieldnames}

        required = {"title"}
        missing = required - set(norm.keys())
        if missing:
            console.print(f"[red]CSV is missing required column(s):[/] {', '.join(missing)}")
            sys.exit(1)

        def get(row: dict, normalised_key: str) -> str:
            orig = norm.get(normalised_key, "")
            return (row.get(orig) or "").strip()

        for row in reader:
            rows.append({
                "title":          get(row, "title"),
                "author":         get(row, "author"),
                "publisher":      get(row, "publisher"),
                "year_published": _normalise_year(get(row, "year_published")),
                "summary":        get(row, "summary"),
                "isbn":           get(row, "isbn"),
            })

    return rows


@click.command("import")
@click.argument("csv_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--replace", is_flag=True, default=False,
              help="Replace existing records that share an ISBN.")
@click.option("--clear", is_flag=True, default=False,
              help="Delete ALL existing books before importing (clean slate).")
def import_csv(csv_file: Path, replace: bool, clear: bool):
    """
    Import a CSV book list into the SQLite database.

    \b
    CSV must have a header row with at least a 'Title' column.
    Optional columns: Author, Publisher, Year Published, Summary, ISBN.

    \b
    Examples:
        books import my_books.csv
        books import updated_list.csv --replace
        books import fresh_list.csv --clear
    """
    db_path = DB_PATH

    # ── Read CSV ─────────────────────────────────────────────────────────────
    console.print(f"[bold]Reading[/] {csv_file} …")
    rows = _read_csv(csv_file)
    if not rows:
        console.print("[yellow]CSV file contains no data rows.[/]")
        return

    console.print(f"  Found [bold]{len(rows)}[/] record(s).")

    # ── Open / create DB ─────────────────────────────────────────────────────
    conn = get_conn(create=True)

    if clear:
        conn.execute("DELETE FROM books")
        conn.commit()
        console.print("  [yellow]Existing books cleared.[/]")

    # ── Insert rows ───────────────────────────────────────────────────────────
    inserted = skipped = replaced = errors = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Importing …", total=len(rows))

        for r in rows:
            try:
                if replace and r["isbn"]:
                    # Delete existing record with same ISBN, then insert fresh
                    conn.execute("DELETE FROM books WHERE isbn = ?", (r["isbn"],))
                    replaced += 1
                elif r["isbn"]:
                    # Skip if ISBN already present
                    exists = conn.execute(
                        "SELECT 1 FROM books WHERE isbn = ?", (r["isbn"],)
                    ).fetchone()
                    if exists:
                        skipped += 1
                        progress.advance(task)
                        continue

                conn.execute(
                    """
                    INSERT INTO books (title, author, publisher, year_published, summary, isbn)
                    VALUES (:title, :author, :publisher, :year_published, :summary, :isbn)
                    """,
                    r,
                )
                inserted += 1
            except Exception as exc:  # noqa: BLE001
                console.print(f"[red]Error inserting row {r.get('title')!r}:[/] {exc}")
                errors += 1
            finally:
                progress.advance(task)

    conn.commit()
    conn.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    console.print()
    console.print(f"[bold green]✅  Import complete[/] → [bold]{db_path}[/]")
    console.print(f"   Inserted:  [bold]{inserted}[/]")
    if replaced:
        console.print(f"   Replaced:  [bold]{replaced}[/]")
    if skipped:
        console.print(f"   Skipped (duplicate ISBN): [bold]{skipped}[/]")
    if errors:
        console.print(f"   [red]Errors:    {errors}[/]")
    total = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] if not conn.close else inserted
    console.print(f"   [bold]Total:     {total}[/]")