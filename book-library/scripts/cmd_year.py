"""
books year – Search books by publication year or year range.

Accepts:
  - A single year                  : books year 1984
  - A range with --to              : books year 1980 --to 1989
  - "since" shorthand              : books year 2020 --to 9999
  - Before shorthand               : books year 0 --to 1950
"""

from __future__ import annotations

import click

from scripts.utils import console, get_conn, print_books


@click.command()
@click.argument("year", type=int)
@click.option("--to", "year_to", type=int, default=None,
              help="End of year range (inclusive). Omit for exact year match.")
@click.option("--summary", "-s", is_flag=True, default=False,
              help="Include the summary column in output.")
@click.option("--limit", "-n", default=100, show_default=True, help="Maximum rows to return.")
def year(year: int, year_to: int | None, summary: bool, limit: int):
    """
    Search books by publication YEAR or year range.

    \b
    Examples:
        books year 1984
        books year 1990 --to 1999
        books year 2015 --to 2024 --summary
    """
    conn = get_conn()

    if year_to is None:
        # Exact year match
        label = str(year)
        rows = conn.execute(
            "SELECT * FROM books WHERE year_published = ? ORDER BY title COLLATE NOCASE LIMIT ?",
            (year, limit),
        ).fetchall()
    else:
        if year_to < year:
            console.print("[red]--to year must be >= start year.[/]")
            raise SystemExit(1)
        label = f"{year} – {year_to}"
        rows = conn.execute(
            """
            SELECT * FROM books
            WHERE year_published BETWEEN ? AND ?
            ORDER BY year_published, title COLLATE NOCASE
            LIMIT ?
            """,
            (year, year_to, limit),
        ).fetchall()

    conn.close()

    console.print(f"\n[bold]Year search:[/] [italic]{label}[/]")
    print_books(rows, show_summary=summary)
