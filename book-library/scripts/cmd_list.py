"""
books list – Browse all books with sorting and pagination.

Useful for exploring the full library or getting an alphabetical listing
without a specific search query.
"""

from __future__ import annotations

import click

from scripts.utils import console, get_conn, print_books

SORT_OPTIONS = {
    "title":     "title COLLATE NOCASE",
    "author":    "author COLLATE NOCASE, title COLLATE NOCASE",
    "year":      "year_published, title COLLATE NOCASE",
    "publisher": "publisher COLLATE NOCASE, title COLLATE NOCASE",
}


@click.command("list")
@click.option("--sort", "-s", default="title",
              type=click.Choice(list(SORT_OPTIONS.keys())), show_default=True,
              help="Sort order.")
@click.option("--limit", "-n", default=50, show_default=True, help="Maximum rows to return.")
@click.option("--offset", "-o", default=0, show_default=True, help="Skip N rows (for pagination).")
@click.option("--summary", is_flag=True, default=False,
              help="Include the summary column in output.")
def list_books(sort: str, limit: int, offset: int, summary: bool):
    """
    List all books (paginated), sorted by the chosen field.

    \b
    Examples:
        books list
        books list --sort year --limit 20
        books list --sort author --offset 50 --limit 25
    """
    conn = get_conn()
    order = SORT_OPTIONS[sort]
    total = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    rows = conn.execute(
        f"SELECT * FROM books ORDER BY {order} LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    conn.close()

    end = min(offset + limit, total)
    console.print(f"\n[bold]All books[/]  (sorted by [italic]{sort}[/], "
                  f"showing {offset + 1}–{end} of {total})")
    print_books(rows, show_summary=summary)

    if end < total:
        console.print(
            f"  [dim]…{total - end} more. Use [/][bold]--offset {end}[/][dim] to see the next page.[/]\n"
        )
