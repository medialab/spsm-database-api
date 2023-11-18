from typing import List

from rich import print
from rich.console import Console
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

        # Set up the columns' select statement
        selected_columns = self.make_selection()
        statement = select(*selected_columns)

        # Execute the selection and write to outfile
        self.select(statement=statement)

    def make_selection(self):
        columns = {c.name: c for c in self.table.columns}
        selected_columns = {}
        still_selecting = True
        while still_selecting:
            Console().clear()
            print("Currently selected: ", set(selected_columns.keys()))
            prompt_choices = columns.copy()
            {prompt_choices.pop(name) for name in selected_columns.keys()}
            self.render_table(selectable_columns=list(prompt_choices.keys()))
            selected_column_name = Prompt.ask(
                "Column", choices=list(prompt_choices.keys()), show_choices=False
            )
            selected_columns.update(
                {selected_column_name: columns[selected_column_name]}
            )
            print("Selected: ", set(selected_columns.keys()))
            still_selecting = Confirm.ask("Do you want to select more columns?")
        columns = list(selected_columns.values())
        selection = []
        for column in columns:
            selection.append(getattr(self.table.c, column.name))
        return selection

    def render_table(self, selectable_columns: List[str]):
        rich_table = RichTable(title="Column options")
        rich_table.add_column(header="names")
        [rich_table.add_row(name) for name in selectable_columns]
        console = Console()
        console.print(rich_table)
