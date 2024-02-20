import csv
from typing import List

from rich.console import Console
from rich.padding import Padding
from rich.prompt import Confirm
from sqlalchemy import Engine, Table, func, select
from sqlalchemy.sql.expression import Select

from src.constants import PARTITION_SIZE, ProgressBar, Spinner
from src.params import ColumnParamSelector, convert_table_param, outfile_param


class Downloader:
    engine: Engine
    console: Console
    table: Table
    headers: List
    select_statement: Select

    def __init__(
        self,
        engine: Engine,
        console: Console,
        select_all: bool | None = False,
        table_name: str | None = None,
    ) -> None:
        self.engine = engine
        self.console = console
        self.table = convert_table_param(
            engine=engine, console=console, table_name=table_name
        )
        self.headers = [str(c.name) for c in self.table.columns]

        # If not all the columns should be downloaded, ask which and build a statement
        if not select_all:
            if Confirm.ask("Do you want to download the whole table?"):
                self.select_statement = select(self.table)
            else:
                columns = ColumnParamSelector(engine, console, self.table)
                self.headers = [str(c.name) for c in columns.selected]
                self.select_statement = select(*columns.selected)
        # Otherwise, if all the columns are to be downloaded, use the default statement
        else:
            self.select_statement = select(self.table)

    def count_rows(self) -> int:
        # Count the table rows (for the progress bar's total)
        count_statement = select(func.count()).select_from(self.table)
        count = 0
        with Spinner(
            console=self.console
        ) as p, self.engine.connect().execution_options(
            postgresql_readonly=True
        ) as cur:
            self.console.print("")
            p.add_task("[yellow]Counting rows")
            try:
                for result in cur.execute(count_statement):
                    count = result[0]
            except KeyboardInterrupt:
                pass
        return count

    def write_results(self, outfile: str | None):
        self.console.clear()
        self.console.rule("[bold blue]Table")
        self.console.print("{}".format(self.table.name))
        self.console.rule("[bold blue]Selected columns")
        self.console.print("{}\n".format(", ".join(self.headers)))
        outfile_path = outfile_param(outfile=outfile)
        total = self.count_rows()
        with open(outfile_path, "w") as f, ProgressBar(console=self.console) as p:
            writer = csv.writer(f)
            writer.writerow(self.headers)
            self.console.print("")
            t = p.add_task("[green]Downloading", total=total)
            with self.engine.connect().execution_options(
                postgresql_readonly=True, yield_per=PARTITION_SIZE
            ).execute(self.select_statement) as result:
                for partition in result.partitions():
                    for row in partition:
                        writer.writerow(row)
                        p.advance(t)
        self.console.print(
            f"\nFinished downloading table.\nFind the written file here: '{outfile_path.absolute()}'\n"
        )
