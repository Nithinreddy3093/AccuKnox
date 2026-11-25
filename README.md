# AccuKnox Assessment 1

This repository implements the three requested data workflows: fetch book records from a REST API and persist/display them in SQLite; retrieve student scores from an API, calculate their arithmetic mean, and create a bar chart; and import user name/email rows from CSV into SQLite.

## Requirements and documented assumptions

- Python 3.10 or newer.
- The prompt does not name a books API. This solution uses the [Open Library Search API](https://openlibrary.org/dev/docs/api/search) (`/search.json`), whose documented response includes `docs` records with `key`, `title`, `author_name`, and `first_publish_year`. Open Library labels this API experimental, so its availability or schema may change.
- The prompt does not provide a scores API URL or response schema. For a runnable public source, this solution uses the [Catalyst Programmers demo student API](https://catalystprogrammers.in/dummy_api/), which returns fictional student records and a numeric `score` inside a `data` array. Its list endpoint supports `limit=50`, enough for the dataset. The command also accepts the assignment's generic JSON array shape `[{"student":"Asha","score":86}]`. Scores must be finite non-negative numbers; no maximum score is assumed.
- The CSV must have `name` and `email` columns. Email addresses are normalized to lowercase and treated as unique; re-import updates the name for an existing email. This makes repeated imports idempotent.
- A missing book author is stored as `Unknown`; a missing publication year is stored as SQL `NULL`.
- These are local assignment scripts, not a network service. No credentials are needed for the selected books endpoint.

## Install

From the repository root in PowerShell:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

On systems where `py` is unavailable, use the installed Python 3.10+ executable to create the virtual environment.

The database defaults to `assessment1.sqlite3` in the current directory. Set `ASSESSMENT1_DB` to choose a different default database. Each command also accepts `--db PATH`.

## Run the workflows

### 1. Fetch, store, and display books

```powershell
assessment1 books --query "artificial intelligence" --limit 10
```

The command makes an HTTP GET request to Open Library, validates the response, inserts or updates records using each work key, then prints the stored books. You can override the API base with `--api-url` when using a compatible endpoint.

### 2. Fetch scores, calculate average, and chart

Fetch the score records from the configured demo endpoint and generate a chart:

```powershell
assessment1 scores --chart scores.png
```

The default URL is `https://catalystprogrammers.in/dummy_api/get-students?page=1&limit=50`. Its response wraps student records in a `data` array and uses `name` and `score` fields. The adapter also accepts the simple response shape below. You can override the default endpoint with `--api-url`.

Generic response shape:

```json
[
  {"student": "Asha", "score": 86},
  {"student": "Dev", "score": 74}
]
```

The command prints the mean of the API's `score` values to two decimal places and writes a PNG bar chart with an average reference line. The default provider describes its data as fake demo student records, so the video and written response should call them demo scores, not real student results. If the API uses another field shape, update the parser to that documented contract rather than silently guessing.

### 3. Import users from CSV

Create a UTF-8 CSV with a header row:

```csv
name,email
Asha Rao,asha@example.com
Dev Mehta,dev@example.com
```

Then run:

```powershell
assessment1 import-users users.csv
```

The importer validates the entire file before writing, uses parameterized SQL, and commits the batch in a SQLite transaction.

## Architecture

```text
CLI
├── books.py  -> HTTP JSON client -> book validation -> SQLite books table -> console display
├── scores.py -> HTTP JSON client -> score validation -> arithmetic mean -> PNG chart
└── users.py  -> CSV parser -> row validation -> parameterized SQLite insert/upsert
                       db.py owns schema setup and transaction-scoped connections
```

The HTTP client uses Python's standard library, a 15-second timeout, a 2 MiB response cap, HTTP(S)-only URLs, and JSON content/decoding checks. SQLite statements bind values instead of interpolating user-controlled values. The importer does not write any rows if input validation fails.

## Tests

```powershell
python -m pytest
```

Tests cover API payload mapping, malformed score/book records, a local HTTP score endpoint, mean calculation, chart creation, SQLite upsert behavior, CSV validation, and all-or-nothing handling of invalid CSV rows. Tests do not depend on an external API or internet connection.

## Security and limitations

- External API data is untrusted and validated before it is stored or plotted.
- Requests use timeouts and bounded response reads to limit hanging or oversized responses.
- SQL uses bound parameters; CSV text is never executed as SQL.
- User input controls API URLs only in a local CLI run. If this code is later exposed as a network service, add destination allowlisting and SSRF protections, authentication, rate limits, and audit logging.
- Email checks are basic syntax checks, not proof that an address exists. Score upper bounds are intentionally not enforced because the prompt does not define a grading scale.
- Open Library identifies its Search API as experimental; isolate API-specific parsing in `books.py` so changes can be handled in one place.


