"""
Book Library CLI – main entry point.

Usage:
    books import  <csv-file>          [--replace] [--clear]
    books search  <query...>          [--summary] [--limit N]
    books author  <name...>           [--summary] [--limit N]
    books title   <title...>          [--summary] [--limit N]
    books isbn    <isbn>              [--summary]
    books year    <year> [--to YEAR]  [--summary] [--limit N]
    books list                        [--sort FIELD] [--limit N] [--offset N]
    books stats                       [--top N]
"""

import click

from scripts.cmd_import import import_csv
from scripts.cmd_search import search
from scripts.cmd_author import author
from scripts.cmd_title  import title
from scripts.cmd_isbn   import isbn
from scripts.cmd_year   import year
from scripts.cmd_list   import list_books
from scripts.cmd_stats  import stats


@click.group()
@click.version_option("1.0.0", prog_name="books")
def cli():
    """
    \b
    📚  Personal Book Library – search your reading list from the terminal.
    Backed by SQLite; import from CSV with `books import`.
    """


cli.add_command(import_csv, name="import")
cli.add_command(search)
cli.add_command(author)
cli.add_command(title)
cli.add_command(isbn)
cli.add_command(year)
cli.add_command(list_books, name="list")
cli.add_command(stats)

if __name__ == "__main__":
    cli()
