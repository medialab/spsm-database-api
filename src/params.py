import csv
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import casanova
import click
import yaml
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Confirm, InvalidResponse, Prompt
from rich.table import Table as RichTable
from sqlalchemy import Column, Engine, MetaData, Table, inspect

from src.constants import Spinner
from src.dynamic_sql import drop_table


class ConnectionParams:
    def __init__(
        self,
        username: str | None,
        password: str | None,
        database: str,
        host: str,
        port: int,
    ) -> None:
        self.username = username
        self.password = password
        self.database = database
        self.host = host
        self.port = port

        console = Console()
        console.clear()
        table = self.generate_table()
        console.print(table)

        while not self.database:
            self.database = click.prompt(
                text="Database Name", hide_input=False, type=str
            )
            console.clear()
            table = self.generate_table()
            console.print(table)

        while not self.host:
            self.host = click.prompt(text="Host", hide_input=False, type=str)
            console.clear()
            table = self.generate_table()
            console.print(table)

        while not self.port:
            self.port = click.prompt(text="Port", hide_input=False, type=str)
            console.clear()
            table = self.generate_table()
            console.print(table)

        while not self.username:
            self.username = click.prompt(text="Username", hide_input=False, type=str)
            console.clear()
            table = self.generate_table()
            console.print(table)

        if not self.password:
            self.password = click.prompt(
                text="Password", hide_input=True, type=str, default=""
            )
            console.clear()
            table = self.generate_table()
            console.print(table)

    def generate_table(self):
        table = RichTable()
        table.add_column("[blue]Parameter")
        table.add_column("[green]User input")
        table.add_row("Database", self.database)
        table.add_row("Host", self.host)
        table.add_row("Port", str(self.port))
        table.add_row("Username", self.username)
        if self.password:
            password_string = "*****"
        else:
            password_string = None
        table.add_row("Password", password_string)
        return table


def convert_table_param(
    engine: Engine, console: Console | None = None, table_name: str | None = None
) -> Table:
    if not console:
        console = Console()
    schema_metadata = MetaData()
    if not table_name:
        tables_in_database = inspect(engine).get_table_names()
        rich_table = RichTable(title="Table options")
        rich_table.add_column(header="names")
        [rich_table.add_row(name) for name in tables_in_database]
        console.print(rich_table)
        table_name = Prompt.ask(
            "Table name", choices=tables_in_database, show_choices=False
        )
    table_object = Table(table_name, schema_metadata, autoload_with=engine)
    return table_object


class ColumnParamSelector:
    console: Console
    engine: Engine
    table: Table
    selected_column_names: List[str]
    table_column_names: List[str]

    def __init__(self, engine: Engine, console: Console, table: Table) -> None:
        self.console = console
        self.table = table
        self.engine = engine
        self.selected_column_names = []
        self.table_column_names = [str(c.name) for c in table.columns]

        self.make_selection(self.table_column_names)
        still_selecting = Confirm.ask("Do you want to select more columns?")
        while still_selecting:
            self.make_selection(self.table_column_names)
            still_selecting = Confirm.ask("Do you want to select more columns?")

    def make_selection(self, columns_to_choose_from: List):
        self.show_options()
        # Prompt the user to select a column
        selection = Prompt.ask(
            "Column to select", choices=columns_to_choose_from, show_choices=False
        )
        # Append the user's input to the list of selected columns
        self.selected_column_names.append(selection)

    def show_options(self):
        self.console.clear()

        # Build table to show the columns already selected
        table_showing_selection = RichTable(title="Selected")
        table_showing_selection.add_column("Columns")
        [table_showing_selection.add_row(c) for c in self.selected_column_names]

        # Build table to show the columns not selected
        columns_to_choose_from = set(self.table_column_names).difference(
            self.selected_column_names
        )
        table_showing_not_selected = RichTable(title="Remaining")
        table_showing_not_selected.add_column("Columns")
        [table_showing_not_selected.add_row(c) for c in columns_to_choose_from]

        # Group tables together and print
        panel_group = Group(
            table_showing_not_selected,
            table_showing_selection,
        )
        self.console.print(Panel(panel_group))

    @property
    def selected(self) -> List[Column]:
        return [
            getattr(self.table.c, column_name)
            for column_name in self.selected_column_names
        ]


def outfile_param(outfile: str | None) -> Path:
    while not outfile:
        outfile = click.prompt(
            text="Outfile", type=click.Path(file_okay=True, dir_okay=False)
        )
    return Path(outfile)


def new_table_param(console: Console, table_name: str | None, engine: Engine) -> str:
    while not table_name:
        proposed_new_table_name = Prompt.ask("[yellow]New table name", console=console)
        tables_in_database = inspect(engine).get_table_names()
        if proposed_new_table_name in tables_in_database:
            console.print(
                f"[red]\nThe table name '{proposed_new_table_name}' is already used in the database."
            )
            console.print("Current table names: ", sorted(tables_in_database))

            # Check if the user wants to delete the table (if they have permission)
            delete_the_table = Confirm.ask(
                "Assuming you have permission, do you want to delete this table?"
            )
            if delete_the_table:
                try:
                    drop_table(proposed_new_table_name, engine)
                except Exception as e:
                    console.print("[red]You did not delete the table.")
                    print(e)
                else:
                    console.print("[green]You deleted the table.")
                    table_name = proposed_new_table_name

        elif proposed_new_table_name.startswith(
            ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
        ):
            console.print(
                f"[red]\nThe table name '{proposed_new_table_name}' starst with a number, which is prohibited in PostgreSQL.",
                "\nPick a name that starts with a letter or an underscore.\n",
            )
        else:
            table_name = proposed_new_table_name
    return table_name


def infile_params(console: Console, infile: str | None):
    while not infile:
        proposed_infile = Prompt.ask("[yellow]Data file", console=console)
        if Path(proposed_infile).is_file():
            infile = proposed_infile
        else:
            console.print("[red]File not found. Please enter a valid file.\n")
    filepath = Path(infile)

    with Spinner as p:
        p.add_task("Counting file length")
        total = casanova.count(filepath)

    with open(filepath, "r") as f:
        reader = casanova.reader(f)
        headers = reader.fieldnames
        if not headers:
            raise KeyError("\nFile needs to have column headers.\n")
        infile_columns = headers

    return filepath, infile_columns, total


def mapping_yaml_params(console: Console, mapping_yaml: str | None):
    while not mapping_yaml:
        proposed_filepath = Prompt.ask("[yellow]YAML mapping file", console=console)
        if Path(proposed_filepath).is_file():
            mapping_yaml = proposed_filepath
        else:
            console.print("[red]File not found. Please enter a valid file.\n")

    with open(mapping_yaml, "r") as f:
        yaml_data = yaml.safe_load(f)
        primary_key = yaml_data["pk"]
        columns = yaml_data["columns"]
        if not primary_key in columns.keys():
            raise KeyError("\nThe primary key needs to be one of the columns.\n")
        return primary_key, columns
