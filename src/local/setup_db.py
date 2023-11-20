from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, Prompt

CREATE = "CREATE TABLE %s AS SELECT * FROM read_csv_auto('%s', HEADER=True%s)"


def create_connection(db_path: str | None) -> str:
    Console().clear()
    if db_path:
        return db_path
    else:
        if Confirm.ask("Do you want to save the database to a file?"):
            db_path = Prompt.ask("Path")
            for p in Path(db_path).parents:
                assert p.is_dir()
        else:
            db_path = ":memory:"
        return db_path
