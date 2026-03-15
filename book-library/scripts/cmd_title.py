"""
books title – Search books by title.

Performs a case-insensitive partial match. Multiple words are matched
with AND logic across the title column.
"""

from __future__ import annotations

import click

from scripts.utils import console, get_conn, print_books, rows_to_dicts, output_json, logger


@click.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--summary", "-s", is_flag=True, default=False,
              help="Include the summary column in output.")
@click.option("--limit", "-n", default=50, show_default=True, help="Maximum rows to return.")
@click.option("--json", "as_json", is_flag=True, default=False,
              help="Output results as JSON.")
def title(query: tuple[str, ...], summary: bool, limit: int, as_json: bool):
    """
    Search books by TITLE (partial, case-insensitive).

    \b
    Examples:
        books title "Lord of the Rings"
        books title clean code
        books title hobbit --summary
        books title clean code --json
    """
    terms = " ".join(query).strip()
    words = terms.split()

    conn = get_conn()
    sql = "SELECT * FROM books WHERE "
    sql += " AND ".join("title LIKE ? COLLATE NOCASE" for _ in words)
    sql += " ORDER BY title COLLATE NOCASE LIMIT ?"

    params = [f"%{w}%" for w in words] + [limit]
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    logger.debug("title query=%r  results=%d", terms, len(rows))
    if as_json:
        output_json(rows_to_dicts(rows))
    else:
        console.print(f"\n[bold]Title search:[/] [italic]{terms}[/]")
        print_books(rows, show_summary=summary)
