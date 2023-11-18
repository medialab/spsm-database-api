from typing import List

from rich import print
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table as RichTable
from sqlalchemy import Engine, select

from src.download.utils import Download


class DownloadColumns(Download):
    def __init__(
        self, engine: Engine, table_name: str | None, download_directory: str
    ) -> None:
        # Initialize the base Download class
        super().__init__(engine, table_name, download_directory)
        self.table_columns = [str(c.name) for c in self.table.columns]
        self.outfile = self.outdir.joinpath("selection_" + self.table.name + ".csv")

        # Set up the columns' select statement
        statement = self.make_selection()
        print(statement)

        # Execute the selection and write to outfile
        self.select(statement=statement)

    def make_selection(self):
        self.console = Console()

        selected_columns = []
        remaining_columns = self.display_choices(selected_columns=selected_columns)
        selection = Prompt.ask(
            "Column to select", choices=remaining_columns, show_choices=False
        )
        selected_columns.append(selection)

        still_selecting = Confirm.ask("Do you want to select more columns?")

        while still_selecting:
            remaining_columns = self.display_choices(selected_columns=selected_columns)
            selection = Prompt.ask(
                "Column to select", choices=remaining_columns, show_choices=False
            )
            selected_columns.append(selection)
            still_selecting = Confirm.ask("Do you want to select more columns?")

        self.display_choices(selected_columns=selected_columns)

        return self.make_statement(selected_columns)

    def display_choices(self, selected_columns: List[str]) -> List[str]:
        self.console.clear()

        remaining_columns = self.determine_remaining(selected_columns)
        remaining_table = RichTable(title="Remaining")
        remaining_table.add_column("Columns")
        [remaining_table.add_row(c) for c in remaining_columns]

        selected_table = RichTable(title="Selected")
        selected_table.add_column("Columns")
        [selected_table.add_row(c) for c in selected_columns]

        panel_group = Group(
            remaining_table,
            selected_table,
        )
        self.console.print(Panel(panel_group))

        return remaining_columns

    def determine_remaining(self, selected_columns: List[str]) -> List[str]:
        return [c for c in self.table_columns if c not in selected_columns]

    def make_statement(self, selected_columns: List[str]):
        columns = []
        for column_name in selected_columns:
            columns.append(getattr(self.table.c, column_name))
        return select(*columns)
