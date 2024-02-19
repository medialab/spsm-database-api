from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

PARTITION_SIZE = 10_000

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
