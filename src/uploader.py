import csv
from typing import List

import casanova
from rich.console import Console
from rich.prompt import Confirm
from sqlalchemy import Engine, Table, func, select
from sqlalchemy.sql.expression import Select

from src.constants import PARTITION_SIZE, ProgressBar, Spinner
from src.dynamic_sql import Base, create_table
from src.params import infile_params, mapping_yaml_params, new_table_param


class Uploader:
    engine: Engine
    console: Console
    table_name: str

    def __init__(
        self,
        engine: Engine,
        console: Console,
        table_name: str | None = None,
    ) -> None:
        self.engine = engine
        self.console = console

        self.table_name = new_table_param(
            table_name=table_name, engine=engine, console=console
        )

    def create_table(self, infile: str | None, mapping_yaml: str | None):
        # Parse the structure of the input CSV file
        infile_path, infile_columns, infile_total = infile_params(
            console=self.console, infile=infile
        )

        # Parse the structure of the data mapping YAML file
        primary_key, mapping_columns = mapping_yaml_params(
            console=self.console, mapping_yaml=mapping_yaml
        )

        # Validate the data file and the data mapping file information
        assert sorted(mapping_columns.keys()) == sorted(infile_columns)
        counter = 0
        with casanova.reader(infile_path) as reader, ProgressBar as p:
            t = p.add_task("[yellow]Validating input file")
            for cell in reader.cells(primary_key, with_rows=False):
                counter += 1
                p.advance(t)
                if cell != "":
                    raise ValueError(f"\nThe primary key at row {counter} is empty.\n")

        # Create a table with the validated schema
        self.table = create_table(
            table_name=self.table_name,
            mapping_yaml=mapping_columns,
            primary_key=primary_key,
        )
        Base.metadata.create_all(self.engine)
