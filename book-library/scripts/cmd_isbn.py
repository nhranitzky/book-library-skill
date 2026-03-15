"""
books isbn – Look up a book by its ISBN.

Supports both ISBN-10 and ISBN-13 (and any other ISBN variant stored in
your CSV). Hyphens and spaces are stripped before matching so that
"978-3-16-148410-0" and "9783161484100" both work.
"""

from __future__ import annotations

import click

from scripts.utils import console, get_conn, print_books, rows_to_dicts, output_json, logger


def _normalise_isbn(raw: str) -> str:
    """Strip hyphens and whitespace from an ISBN string."""
    return raw.replace("-", "").replace(" ", "").strip()


@click.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--summary", "-s", is_flag=True, default=False,
              help="Include the summary column in output.")
@click.option("--json", "as_json", is_flag=True, default=False,
              help="Output results as JSON.")
def isbn(query: tuple[str, ...], summary: bool, as_json: bool):
    """
    Look up a book by ISBN (hyphens/spaces are ignored).

    \b
    Examples:
        books isbn 978-0-06-112008-4
        books isbn 9780061120084
        books isbn 0-06-112008-1
        books isbn 978-0-06-112008-4 --json
    """
    raw = " ".join(query)
    normalised = _normalise_isbn(raw)

    conn = get_conn()

    # Match both with and without hyphens by stripping from the stored value too
    rows = conn.execute(
        "SELECT * FROM books WHERE REPLACE(REPLACE(isbn, '-', ''), ' ', '') = ?",
        (normalised,),
    ).fetchall()

    # Fallback: partial match (in case the stored ISBN has a different format)
    if not rows:
        rows = conn.execute(
            "SELECT * FROM books WHERE isbn LIKE ?", (f"%{normalised}%",)
        ).fetchall()

    conn.close()

    logger.debug("isbn query=%r  normalised=%r  results=%d", raw, normalised, len(rows))
    if as_json:
        output_json(rows_to_dicts(rows))
    else:
        console.print(f"\n[bold]ISBN search:[/] [italic]{raw}[/]")
        print_books(rows, show_summary=summary)
