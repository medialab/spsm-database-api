import csv
from pathlib import Path
from typing import List

from rich import print
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Prompt
from rich.table import Table as RichTable
from sqlalchemy import Engine, MetaData, Table, func, inspect, select
from sqlalchemy.sql.schema import Table
from sqlalchemy.sql.selectable import Select

from src.constants import PARTITION_SIZE

Spinner = Progress(
    TextColumn("[progress.description]{task.description}"),
    SpinnerColumn(),
    TimeElapsedColumn(),
)

ProgressBar = Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    MofNCompleteColumn(),
    TimeElapsedColumn(),
)


class Download:
    def __init__(
        self, engine: Engine, table_name: str | None, download_directory: str
    ) -> None:
        self.engine = engine
        self.outdir = Path(download_directory)
        self.outdir.mkdir(exist_ok=True)
        self.table = self.confirm_table(table_name=table_name)
        self.outfile = self.setup_outfile()

    def confirm_table(self, table_name: str | None) -> Table:
        metadata = MetaData()
        if not table_name:
            table_names = inspect(self.engine).get_table_names()
            self.list_table_options(table_names)
            table_name = Prompt.ask(
                "Table name", choices=table_names, show_choices=False
            )
        table = Table(table_name, metadata, autoload_with=self.engine)
        return table

    def list_table_options(self, table_names: List) -> None:
        table = RichTable(title="Table options")
        table.add_column(header="names")
        [table.add_row(name) for name in table_names]
        console = Console()
        console.print(table)

    def count_rows(self, id_name: str) -> int:
        count = 0
        with self.engine.connect().execution_options(postgresql_readonly=True) as conn:
            with Spinner as progress:
                progress.add_task("[yellow]Counting rows")
                try:
                    for res in conn.execute(
                        select(func.count(getattr(self.table.c, id_name)))
                    ):
                        count = res[0]
                except KeyboardInterrupt:
                    pass
        return count

    def setup_outfile(self) -> Path:
        outfile = self.outdir.joinpath(self.table.name + ".csv")
        return outfile

    def select(self, statement: Select):
        headers = [c.name.split(".")[-1] for c in statement.columns]
        id_name = "id"
        if "science_feedback" in str(self.table.name):
            id_name = "claim_appearance_id"
        self.count = self.count_rows(id_name)
        with open(self.outfile, "w") as f, ProgressBar as progress:
            writer = csv.writer(f)
            writer.writerow(headers)
            t = progress.add_task("[green]Downloading", total=self.count)
            with self.engine.connect().execution_options(
                postgresql_readonly=True, yield_per=PARTITION_SIZE
            ).execute(statement) as result:
                for partition in result.partitions():
                    for row in partition:
                        writer.writerow(row)
                        progress.advance(t)
        print(f"\nFinished downloading table.\nFile: '{self.outfile.absolute()}'\n")
