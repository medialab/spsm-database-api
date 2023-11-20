from pathlib import Path
from typing import Dict, Tuple

import click
import duckdb
from duckdb import DuckDBPyConnection
from rich import print
from rich.console import Console, Group
from rich.padding import Padding
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Prompt
from rich.table import Table as RichTable
from rich.text import Text
from sql_metadata import Parser

from src.local.exceptions import MissingRelationReferencedInQuery


class ExecuteSQLFile:
    def __init__(self, query_file: str | None, outfile: str | None):
        self.console = Console()
        self.console.clear()
        self.query_file = query_file
        self.outfile = outfile
        self.tables_in_query = ""
        self.generate_param_table()

        if not self.query_file:
            self.query_file = click.prompt(
                "Path to SQL file",
                type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
            )
            while not Path(self.query_file).is_file():
                print("[red]File not found.")
                self.query_file = click.prompt(
                    "Path to SQL file",
                    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
                )
        self.generate_param_table()

        if not self.outfile:
            self.outfile = click.prompt("Path to CSV out-file", type=str)
            if not self.outfile:
                raise ValueError
            for p in Path(self.outfile).parents:
                if not p.is_dir():
                    raise NotADirectoryError(self.outfile)
        self.generate_param_table()

        with open(self.query_file) as f:
            self.query = f.read()
        self.tables_in_query = Parser(self.query).tables

    def add_tables_manually(self):
        tables_in_database = self.connection.execute("SHOW TABLES;").fetchall()
        if not len(tables_in_database) == 0:
            tables_in_database = [t[0] for t in tables_in_database]
        for table_in_query in self.tables_in_query:
            self.console.clear()
            self.display_missing_relations()
            if table_in_query not in tables_in_database:
                print(
                    f"The relation '{table_in_query}' is not in your DuckDB database."
                )
                relation_file = Prompt.ask("Enter a filename for this relation")
                while not Path(relation_file).is_file():
                    print("[red]File not found.")
                    relation_file = Prompt.ask(
                        "Enter a valid filename for this relation"
                    )

                self.create_table(infile=relation_file, table_name=table_in_query)

    def create_table(self, infile: str, table_name: str):
        self.console.clear()
        self.console.print(
            Padding(
                Panel.fit(
                    f"Table: '{table_name}'\nFile: '{infile}'", title="Creating table"
                ),
                (1, 4),
            ),
        )
        self.connection.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        compression = ""
        if Path(infile).suffix == ".gz":
            compression = ", COMPRESSION='gzip'"
        CREATE = "CREATE TABLE %s AS SELECT * FROM read_csv_auto('%s', HEADER=True%s)"
        query = CREATE % (table_name, infile, compression)
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            SpinnerColumn(),
            TimeElapsedColumn(),
        ) as progress:
            progress.add_task(f"Creating table '{table_name}'")
            self.connection.execute(query)

    def __call__(self, connection: DuckDBPyConnection, tables: Dict | None = None):
        # Register the DuckDB database connection
        self.connection = connection

        # Add tables to DuckDB database
        if not tables:
            self.add_tables_manually()
        else:
            missing_tables = set(self.tables_in_query).difference(set(tables.keys()))
            if len(missing_tables) > 0:
                raise MissingRelationReferencedInQuery(missing_tables)
            for table_name, infile in tables.items():
                self.create_table(infile=infile, table_name=table_name)

        # Execute the SQL file's query
        self.console.rule("[bold yellow]DuckDB is executing SQL query")
        self.console.print(
            Panel.fit(Text(self.query, justify="left"), title="Query"), justify="center"
        )
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            SpinnerColumn(),
            TimeElapsedColumn(),
        ) as spinner:
            spinner.add_task("Executing query")
            rel = self.connection.sql(self.query)
            rel.write_csv(self.outfile, header=True)  # type:ignore
        self.console.print(f"File written to: '{self.outfile}'", justify="center")
        self.console.rule("[bold blue]Preview")
        print(rel.show())

    def generate_param_table(self):
        def path_to_string(p: Path | None | str) -> str | None:
            if isinstance(p, Path):
                return str(p)
            else:
                return p

        self.console.clear()
        table = RichTable()
        table.add_column("[blue]Parameter")
        table.add_column("[green]User input")
        table.add_row("Outfile", path_to_string(self.outfile))
        table.add_row("Query file", path_to_string(self.query_file))
        self.console.print(table)

    def display_missing_relations(self):
        created_relations = self.connection.execute("SHOW TABLES;").fetchall()
        if len(created_relations) > 0:
            created_relations = [t[0] for t in created_relations]
        table = RichTable(title="Relations in query")
        table.add_column("Relation alias")
        table.add_column("In database")
        for relation in self.tables_in_query:
            if relation in created_relations:
                table.add_row(relation, "[green]True")
            else:
                table.add_row(relation, "[red]False")
        panel_group = Group(
            Panel.fit(Text(self.query, justify="left"), title="Query"),
            table,
        )
        self.console.print(Panel(panel_group))

    def print_table(self, table_name: str):
        table = RichTable(title=table_name, row_styles=["yellow", "green"])
        table.add_column("Column name")
        table.add_column("Row count")
        table.add_column("Mininum value")
        table.add_column("Maximum value")
        rel = duckdb.table(table_name, self.connection)
        for column in rel.columns:
            col_max = rel.max(column).fetchone()
            col_min = rel.min(column).fetchone()
            col_count = rel.count(column).fetchone()
            args = [column]
            for a in [col_count, col_min, col_max]:
                if isinstance(a, Tuple):
                    args.append(str(a[0]))
                else:
                    args.append(None)
            table.add_row(*args)
        print(table)
