"""Command-line interface for the assignment workflows."""
import argparse
import logging
import sqlite3
import sys

from . import books, scores, users
from .db import default_database_path, initialize
from .http_json import ApiError


def build_parser():
    parser = argparse.ArgumentParser(prog="assessment1", description="AccuKnox assignment 1 data workflows")
    parser.add_argument("--db", default=default_database_path(), help="SQLite database path (default: assessment1.sqlite3 or ASSESSMENT1_DB)")
    commands = parser.add_subparsers(dest="command", required=True)
    book_cmd = commands.add_parser("books", help="Fetch books, save to SQLite, and display stored books")
    book_cmd.add_argument("--query", default="artificial intelligence")
    book_cmd.add_argument("--limit", type=int, default=10)
    book_cmd.add_argument("--api-url", default=books.OPEN_LIBRARY_SEARCH_URL)
    score_cmd = commands.add_parser("scores", help="Fetch scores from an API, calculate average, and create a bar chart")
    score_cmd.add_argument("--api-url", default=scores.DEFAULT_SCORE_API_URL,
                           help="HTTP(S) scores API URL (defaults to the documented public demo endpoint)")
    score_cmd.add_argument("--chart", default="student_scores.png")
    user_cmd = commands.add_parser("import-users", help="Import a CSV containing name,email columns into SQLite")
    user_cmd.add_argument("csv_file")
    return parser


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = build_parser().parse_args(argv)
    try:
        initialize(args.db)
        if args.command == "books":
            fetched = books.fetch_books(args.query, args.limit, args.api_url)
            books.store_books(fetched, args.db)
            print(f"Fetched {len(fetched)} book records. Books stored in {args.db}:")
            for row in books.list_books(args.db):
                year = row["publication_year"] if row["publication_year"] is not None else "unknown year"
                print(f"- {row['title']} | {row['author']} | {year}")
        elif args.command == "scores":
            rows = scores.fetch_scores(args.api_url)
            average = scores.create_bar_chart(rows, args.chart)
            print(f"Average score: {average:.2f} (n={len(rows)})")
            print(f"Bar chart saved to {args.chart}")
        elif args.command == "import-users":
            count = users.import_users(args.csv_file, args.db)
            print(f"Imported or updated {count} CSV rows in {args.db}.")
        return 0
    except (ApiError, ValueError, OSError, sqlite3.Error) as exc:
        logging.error("%s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
