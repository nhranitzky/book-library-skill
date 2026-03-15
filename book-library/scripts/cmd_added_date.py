"""
books added-date – Search books by the date they were added.

Accepts an optional date range (from, to).
  - Both provided  : books added between the two dates (inclusive)
  - Only --from    : books added from that date up to today
  - Only --to      : all books added up to that date
  - Neither        : all books with a date_added value

Dates are accepted in any common format (YYYY-MM-DD, DD.MM.YYYY, etc.).
"""

from __future__ import annotations

from datetime import date

import click

from scripts.cmd_import import _normalise_date
from scripts.utils import console, get_conn, print_books, rows_to_dicts, output_json, logger


def _parse_date_option(value: str | None, param_name: str) -> str | None:
    """Validate and normalise a date option; exit with an error if unparseable."""
    if value is None:
        return None
    normalised = _normalise_date(value)
    if normalised is None:
        logger.error("Cannot parse date option %s=%r", param_name, value)
        console.print(f"[red]Cannot parse date for {param_name}:[/] {value!r}")
        raise SystemExit(1)
    return normalised


@click.command("added-date")
@click.option("--from", "date_from", default=None, metavar="DATE",
              help="Start date (inclusive). Omit for no lower bound.")
@click.option("--to", "date_to", default=None, metavar="DATE",
              help="End date (inclusive). Defaults to today when --from is given.")
@click.option("--summary", "-s", is_flag=True, default=False,
              help="Include the summary column in output.")
@click.option("--limit", "-n", default=100, show_default=True, help="Maximum rows to return.")
@click.option("--json", "as_json", is_flag=True, default=False,
              help="Output results as JSON.")
def added_date(date_from: str | None, date_to: str | None, summary: bool, limit: int, as_json: bool):
    """
    Search books by the date they were added.

    \b
    Examples:
        books added-date --from 2024-01-01
        books added-date --from 2024-01-01 --to 2024-12-31
        books added-date --to 2023-12-31
    """
    from_iso = _parse_date_option(date_from, "--from")
    to_iso = _parse_date_option(date_to, "--to")

    # Default --to to today when --from is provided but --to is not
    if from_iso and not to_iso:
        to_iso = date.today().isoformat()

    logger.debug("added-date query: from=%s  to=%s", from_iso, to_iso)

    conn = get_conn()

    if from_iso and to_iso:
        label = f"{from_iso} – {to_iso}"
        rows = conn.execute(
            """
            SELECT * FROM books
            WHERE date_added BETWEEN ? AND ?
            ORDER BY date_added, title COLLATE NOCASE
            LIMIT ?
            """,
            (from_iso, to_iso, limit),
        ).fetchall()
    elif to_iso:
        label = f"up to {to_iso}"
        rows = conn.execute(
            """
            SELECT * FROM books
            WHERE date_added <= ?
            ORDER BY date_added, title COLLATE NOCASE
            LIMIT ?
            """,
            (to_iso, limit),
        ).fetchall()
    else:
        label = "all with date"
        rows = conn.execute(
            """
            SELECT * FROM books
            WHERE date_added IS NOT NULL
            ORDER BY date_added, title COLLATE NOCASE
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    conn.close()

    logger.debug("added-date results=%d  label=%r", len(rows), label)
    if as_json:
        output_json(rows_to_dicts(rows))
    else:
        console.print(f"\n[bold]Added date:[/] [italic]{label}[/]")
        print_books(rows, show_summary=summary)
