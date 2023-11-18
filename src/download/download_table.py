from rich import print
from rich.console import Console
from rich.panel import Panel
from sqlalchemy import Engine

from src.download.utils import Download


class DownloadTable(Download):
    def __init__(
        self, engine: Engine, table_name: str | None, download_directory: str
    ) -> None:
        # Initialize the base Download class
        super().__init__(engine, table_name, download_directory)

        print("\n")
        print(
            Panel.fit(
                f"[red]Table: '{self.table.name}'\n[red]Outfile: '{self.outfile}'",
                title="[green]Download",
            )
        )

        # Set up the table select statement
        select_statement = self.table.select()

        # Execute the selection and write to outfile
        self.select(statement=select_statement)
