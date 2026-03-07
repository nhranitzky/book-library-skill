"""
books stats – Show library statistics and a quick overview.

Reports total book count, unique authors, year range, top authors,
and top publishers.
"""

from __future__ import annotations

import click
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich import box

from scripts.utils import console, get_conn


@click.command()
@click.option("--top", "-n", default=10, show_default=True,
              help="How many top authors / publishers to display.")
def stats(top: int):
    """
    Display library statistics: counts, year range, top authors/publishers.

    \b
    Example:
        books stats
        books stats --top 20
    """
    conn = get_conn()

    total       = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    authors     = conn.execute("SELECT COUNT(DISTINCT author) FROM books WHERE author != ''").fetchone()[0]
    publishers  = conn.execute("SELECT COUNT(DISTINCT publisher) FROM books WHERE publisher != ''").fetchone()[0]
    year_min    = conn.execute("SELECT MIN(year_published) FROM books WHERE year_published IS NOT NULL").fetchone()[0]
    year_max    = conn.execute("SELECT MAX(year_published) FROM books WHERE year_published IS NOT NULL").fetchone()[0]
    no_isbn     = conn.execute("SELECT COUNT(*) FROM books WHERE isbn IS NULL OR isbn = ''").fetchone()[0]

    top_authors = conn.execute(
        """
        SELECT author, COUNT(*) AS cnt
        FROM books WHERE author != ''
        GROUP BY author COLLATE NOCASE
        ORDER BY cnt DESC, author COLLATE NOCASE
        LIMIT ?
        """,
        (top,),
    ).fetchall()

    top_publishers = conn.execute(
        """
        SELECT publisher, COUNT(*) AS cnt
        FROM books WHERE publisher != ''
        GROUP BY publisher COLLATE NOCASE
        ORDER BY cnt DESC, publisher COLLATE NOCASE
        LIMIT ?
        """,
        (top,),
    ).fetchall()

    top_decades = conn.execute(
        """
        SELECT (year_published / 10) * 10 AS decade, COUNT(*) AS cnt
        FROM books
        WHERE year_published IS NOT NULL
        GROUP BY decade
        ORDER BY cnt DESC
        LIMIT ?
        """,
        (top,),
    ).fetchall()

    conn.close()

    # ── Overview panel ────────────────────────────────────────────────────────
    from rich.text import Text
    overview = Text()
    overview.append(f"  📚 Total books:       ", style="bold")
    overview.append(f"{total}\n")
    overview.append(f"  ✍️  Unique authors:     ", style="bold")
    overview.append(f"{authors}\n")
    overview.append(f"  🏢 Unique publishers: ", style="bold")
    overview.append(f"{publishers}\n")
    overview.append(f"  📅 Year range:        ", style="bold")
    overview.append(f"{year_min} – {year_max}\n" if year_min else "unknown\n")
    overview.append(f"  ❓ Missing ISBN:       ", style="bold")
    overview.append(f"{no_isbn}\n")

    console.print()
    console.print(Panel(overview, title="[bold green]Library Overview[/]", expand=False))

    # ── Top authors ───────────────────────────────────────────────────────────
    def rank_table(title: str, rows, label: str) -> Table:
        t = Table(title=title, box=box.SIMPLE, show_header=True, header_style="bold cyan")
        t.add_column("#", justify="right", style="dim", width=3)
        t.add_column(label, style="green")
        t.add_column("Books", justify="right", style="bold")
        for i, row in enumerate(rows, 1):
            t.add_row(str(i), row[0], str(row[1]))
        return t

    author_table    = rank_table(f"Top {top} Authors",    top_authors,    "Author")
    publisher_table = rank_table(f"Top {top} Publishers", top_publishers, "Publisher")
    decade_table    = rank_table(f"Top {top} Decades",    [(f"{r[0]}s", r[1]) for r in top_decades], "Decade")

    console.print(Columns([author_table, publisher_table, decade_table], equal=False, expand=False))
    console.print()
