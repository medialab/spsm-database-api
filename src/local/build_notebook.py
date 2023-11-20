import json
from pathlib import Path

from src.local.notebook_template import write_template


class Notebook:
    def __init__(self, dir: str | None, new: str | None, database: str) -> None:
        if not dir:
            self.dir = Path.cwd()
        elif not Path(dir).is_dir():
            raise NotADirectoryError
        else:
            self.dir = Path(dir)

        if new:
            self.file = Path(new)
        else:
            self.file = self.dir.joinpath("DuckDB_Notebook.ipynb")

        # check if Jupyter notebooks already in directory
        write_new_notebook = True
        if not new:
            for file in self.dir.iterdir():
                if file.is_file():
                    if file.suffix == ".ipynb":
                        write_new_notebook = False
        if write_new_notebook:
            with open(self.file, "w") as f:
                f.write(json.dumps(write_template(database)))
