"""
books author – Search books by author name.

Performs a case-insensitive partial match (LIKE %query%).
Multiple words are matched independently (AND logic), so
"Stephen King" finds rows where the author column contains
both "Stephen" and "King" (in any order).
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
def author(query: tuple[str, ...], summary: bool, limit: int, as_json: bool):
    """
    Search books by AUTHOR name (partial, case-insensitive).

    \b
    Examples:
        books author Tolkien
        books author "Ursula Le Guin"
        books author stephen king --summary
        books author Tolkien --json
    """
    terms = " ".join(query).strip()
    words = terms.split()

    conn = get_conn()
    sql = "SELECT * FROM books WHERE "
    sql += " AND ".join("author LIKE ? COLLATE NOCASE" for _ in words)
    sql += " ORDER BY author COLLATE NOCASE, year_published LIMIT ?"

    params = [f"%{w}%" for w in words] + [limit]
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    logger.debug("author query=%r  results=%d", terms, len(rows))
    if as_json:
        output_json(rows_to_dicts(rows))
    else:
        console.print(f"\n[bold]Author search:[/] [italic]{terms}[/]")
        print_books(rows, show_summary=summary)
