from rich.console import Console
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from src.download.download_params import DownloadParams


def connect_to_database(params: DownloadParams):
    url = URL.create(
        drivername="postgresql",
        username=params.username,
        host=params.host,
        database=params.database,
        password=params.password,
        port=params.port,
    )

    try:
        engine = create_engine(url)
    except Exception as e:
        raise e
    else:
        console = Console()
        console.clear()
        console.rule("[bold blue]Connected to the PostgreSQL database")
        return engine
