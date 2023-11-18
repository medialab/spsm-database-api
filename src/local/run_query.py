from pathlib import Path

import duckdb
from rich import print
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from src.local.setup_db import DB

Spinner = Progress(
    TextColumn("[progress.description]{task.description}"),
    SpinnerColumn(),
    TimeElapsedColumn(),
)


def execute_query(query_file: str, db: DB, outfile: str):
    with open(query_file) as r:
        query = r.read()

    print(Panel.fit(query, title="[red]SQL query"))

    db.insert_tables_manually()

    kwargs = {}
    if Path(outfile).suffix == ".gz":
        kwargs = {"compression": "gzip"}

    with Spinner as progress:
        progress.add_task("Executing and writing query")
        duckdb.query(query=query, connection=db.connection).write_csv(
            str(outfile), header=True, **kwargs
        )
