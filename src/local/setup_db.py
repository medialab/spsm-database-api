from pathlib import Path
from typing import Iterable

import duckdb
from duckdb import DuckDBPyConnection
from rich.console import Console
from rich.prompt import Confirm, Prompt

CREATE = "CREATE TABLE %s AS SELECT * FROM read_csv_auto('%s', HEADER=True%s)"


def create_connection(db_path: str | None) -> DuckDBPyConnection:
    Console().clear()
    if db_path:
        return duckdb.connect(db_path)
    else:
        if Confirm.ask("Do you want to save the database to a file?"):
            db_path = Prompt.ask("Path")
            for p in Path(db_path).parents:
                assert p.is_dir()
        else:
            db_path = ":memory:"
        return duckdb.connect(db_path)
