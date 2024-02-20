from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

PARTITION_SIZE = 10_000


class Spinner:
    def __init__(self, console: Console | None) -> None:
        self.p = Progress(
            TextColumn("[progress.description]{task.description}"),
            SpinnerColumn(),
            TimeElapsedColumn(),
            console=console,
        )

    def __enter__(self):
        return self.p.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.p.__exit__(exc_type, exc_val, exc_tb)


class ProgressBar:

    def __init__(self, console: Console | None = None) -> None:
        self.p = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
        )

    def __enter__(self):
        return self.p.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.p.__exit__(exc_type, exc_val, exc_tb)
