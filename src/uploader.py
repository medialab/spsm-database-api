import casanova
import pyarrow
import pyarrow.csv
from rich.console import Console
from sqlalchemy import Engine, insert
from sqlalchemy.exc import StatementError

from src.constants import ProgressBar
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
        with casanova.reader(infile_path) as reader, ProgressBar(
            console=self.console
        ) as p:
            self.console.print("")
            t = p.add_task("[yellow]Validating input file", total=infile_total)
            for row, cell in reader.cells(primary_key, with_rows=True):
                counter += 1
                p.advance(t)
                if cell == "":
                    raise ValueError(
                        f"\nThe primary key at row {counter} is empty.Row: {row}\n"
                    )

        # Create a table with the validated schema
        self.table = create_table(
            table_name=self.table_name,
            mapping_yaml=mapping_columns,
            primary_key=primary_key,
        )
        Base.metadata.create_all(self.engine)

        # Import the data into the table
        insert_expression = insert(self.table)
        with ProgressBar(
            console=self.console
        ) as p, self.engine.connect() as conn, pyarrow.csv.open_csv(
            infile_path
        ) as reader:
            self.console.print("")
            t = p.add_task("[blue]Inserting data", total=infile_total)

            for next_chunk in reader:
                if next_chunk is None:
                    break
                batch_record = pyarrow.Table.from_batches([next_chunk])
                try:
                    conn.execute(insert_expression, batch_record.to_pylist())
                except StatementError as e:
                    raise e
                else:
                    conn.commit()
                p.advance(t, advance=len(next_chunk))
