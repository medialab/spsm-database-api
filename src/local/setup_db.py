from pathlib import Path
from typing import Iterable

import duckdb
from duckdb import DuckDBPyConnection
from rich import print
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table as RichTable

CREATE = "CREATE TABLE %s AS SELECT * FROM read_csv_auto('%s', HEADER=True%s)"


def setup_connection(db_path: str | None):
    if not db_path:
        if Confirm.ask(
            "Do you want to save the database to a file?\nIf not, everything will be processed in memory."
        ):
            db_path = Prompt.ask("Path")
            for p in Path(db_path).parents:
                assert p.is_dir()
        else:
            db_path = ":memory:"
    return duckdb.connect(db_path)


class DB:
    def __init__(
        self, db_path: str | None, connection: DuckDBPyConnection | None = None
    ) -> None:
        if connection:
            self.connection = connection
        elif db_path:
            self.connection = duckdb.connect(db_path)
        else:
            if Confirm.ask(
                "Do you want to save the database to a file?\nIf not, everything will be processed in memory."
            ):
                db_path = Prompt.ask("Path")
                for p in Path(db_path).parents:
                    assert p.is_dir()
            else:
                db_path = ":memory:"
            self.connection = duckdb.connect(db_path)

    def insert_tables_manually(self):
        if len(self.connection.execute("SHOW TABLES;").fetchall()) == 0:
            self.prompt_to_add_tables()
        will_import_more = True
        while will_import_more:
            Console().clear()
            if Confirm.ask("Do you want to import more tables?"):
                self.prompt_to_add_tables()
            else:
                will_import_more = False

    def prompt_to_add_tables(self):
        table_name = Prompt.ask("\nEnter table name for imported data")
        file_path = Prompt.ask("Enter path to CSV")
        self.read_csv_into_table(table_name=table_name, file=Path(file_path))

    def create(self, table: str, file: str):
        compression = ""
        if Path(file).suffix == ".gz":
            compression = ", COMPRESSION='gzip'"
        query = CREATE % (table, file, compression)
        self.connection.execute(query)

    def read_csv_into_table(self, table_name: str, file: Path):
        file_name = str(file)
        if table_name in self.connection.execute("SHOW TABLES;").fetchall():
            print(f"Table '{table_name}' exists.")
            if not Confirm.ask("Do you want to delete it?"):
                return
            else:
                self.connection.execute(f"DROP TABLE {table_name} CASCADE")
                self.create(table_name, file_name)

        else:
            self.create(table_name, file_name)

        tables = [t[0] for t in self.connection.execute("SHOW TABLES;").fetchall()]
        self.render_table(title="Current tables", l=tables)

    def render_table(self, title: str, l: Iterable[str]):
        rich_table = RichTable(title=title)
        rich_table.add_column(header="names")
        [rich_table.add_row(name) for name in l]
        console = Console()
        print("\n")
        console.print(rich_table)
