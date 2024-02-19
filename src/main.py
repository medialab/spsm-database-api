import click
from rich.console import Console

from src.connect import connect_to_database
from src.download import Downloader
from src.params import ConnectionParams


@click.group()
@click.option("--database", default="spsm-database")
@click.option("--host", default="localhost")
@click.option("--port", default=54321)
@click.option("--username", type=click.STRING)
@click.option("--password", type=click.STRING)
@click.pass_context
def cli(ctx, username, password, database, host, port):
    ctx.ensure_object(dict)
    console = Console()
    params = ConnectionParams(username, password, database, host, port)
    ctx.obj["SQL_ENGINE"] = connect_to_database(params, console)
    ctx.obj["RICH_CONSOLE"] = console


# ----------- UPLOAD COMMAND ----------- #
@cli.command("upload")
@click.pass_context
def upload(ctx):
    engine = ctx.obj["SQL_ENGINE"]
    console = ctx.obj["RICH_CONSOLE"]


# ----------- DOWNLOAD COMMAND ----------- #
@cli.command("download")
@click.option(
    "--table",
    type=click.STRING,
    default="",
    show_default=False,
    help="Name of the table to download",
)
@click.option(
    "--select-all",
    is_flag=True,
    show_default=True,
    default=False,
    help="Download all columns",
)
@click.option("--outfile", type=click.Path(file_okay=True, dir_okay=False))
@click.pass_context
def download(ctx, table: str, outfile: str | None, select_all: bool | None = False):
    engine = ctx.obj["SQL_ENGINE"]
    console = ctx.obj["RICH_CONSOLE"]
    downloader = Downloader(
        engine=engine,
        console=console,
        table_name=table,
        select_all=select_all,
    )
    downloader.write_results(outfile=outfile)


if __name__ == "__main__":
    cli()
