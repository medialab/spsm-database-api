import gzip
from datetime import date
from pathlib import Path
from typing import Tuple

from psycopg2.extensions import connection as Connection
from rich import print
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

progress = Progress(
    TextColumn("[progress.description]{task.description}"),
    SpinnerColumn(),
    TimeElapsedColumn(),
)


def download_table(connection: Connection, table: str, download_directory: str):
    dir_path = Path(download_directory)
    dir_path.mkdir(exist_ok=True)
    validator = TableNameValidator()
    try:
        table_size, size_unit, outfile = validator(table, connection, dir_path)
    except Exception as e:
        raise e
    if not outfile:
        raise FileNotFoundError

    print(
        Panel.fit(
            f"table: '{table}'\nsize: {table_size} {size_unit}",
            title="[yellow]Downloading",
        )
    )

    cursor = connection.cursor()
    with progress as p, gzip.open(outfile, "wb") as f:
        p.add_task(description="[yellow]Downloading...")
        cursor.copy_to(f, table)  # type: ignore

    print(f"\nTable downloaded to CSV file '{outfile}'.\n")


class TableNameValidator:
    def __init__(self) -> None:
        pass

    def __call__(
        self, table_name: str, connection: Connection, download_directory: Path
    ) -> Tuple[int, str, Path] | Tuple[ValueError, None, None]:
        cursor = connection.cursor()
        cursor.execute(
            """
SELECT table_name, pg_size_pretty( pg_total_relation_size(quote_ident(table_name)))
FROM information_schema.tables
WHERE table_schema = 'public'
"""
        )
        tables = {table: size for table, size in cursor.fetchall()}
        if not tables.get(table_name):
            raise ValueError(
                f"\n\nTable '{table_name}' is not one of the database's tables.\nCreated tables are: {list(tables.keys())}\n"
            )
        outfile = download_directory.joinpath(f"{table_name}_{date.today()}.csv.gz")
        table_size = int(tables[table_name].split()[0])
        size_unit = tables[table_name].split()[1]
        return table_size, size_unit, outfile
