"""
books search – Full-text keyword search across all fields.

Searches title, author, publisher, and summary simultaneously.
Each word in the query is matched independently (AND logic) across
all fields combined (OR within a single word, AND between words).

This is the "I'm not sure where the info is" command.
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
def search(query: tuple[str, ...], summary: bool, limit: int, as_json: bool):
    """
    Keyword search across ALL fields (title, author, publisher, summary).

    \b
    Examples:
        books search dragon
        books search "machine learning" python
        books search tolkien ring --summary
        books search tolkien --json
    """
    terms = " ".join(query).strip()
    words = terms.split()

    conn = get_conn()

    # Each word must appear in at least one of the text fields (AND between words)
    per_word_clause = " AND ".join(
        """(
            title     LIKE ? COLLATE NOCASE OR
            author    LIKE ? COLLATE NOCASE OR
            publisher LIKE ? COLLATE NOCASE OR
            summary   LIKE ? COLLATE NOCASE
        )"""
        for _ in words
    )
    sql = f"SELECT * FROM books WHERE {per_word_clause} ORDER BY title COLLATE NOCASE LIMIT ?"
    # Each word needs 4 params (title / author / publisher / summary)
    params = [f"%{w}%" for w in words for _ in range(4)] + [limit]

    rows = conn.execute(sql, params).fetchall()
    conn.close()

    logger.debug("search query=%r  results=%d", terms, len(rows))
    if as_json:
        output_json(rows_to_dicts(rows))
    else:
        console.print(f"\n[bold]Keyword search:[/] [italic]{terms}[/]")
        print_books(rows, show_summary=summary)
