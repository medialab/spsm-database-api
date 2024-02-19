import subprocess

import click

from src.connect import connect_to_database
from src.constants import (
    POSTGRESQL_DB_NAME,
    POSTGRESQL_REROUTED_HOST,
    POSTGRESQL_REROUTED_PORT,
)
from src.download.download_columns import DownloadColumns
from src.download.download_params import DownloadParams
from src.download.download_table import DownloadTable


@click.group()
def cli():
    pass


# ---------------------------------------- #
# ----------- DOWNLOAD COMMAND ----------- #
@cli.group()
@click.option("--database", default=POSTGRESQL_DB_NAME)
@click.option("--host", default=POSTGRESQL_REROUTED_HOST)
@click.option("--port", default=POSTGRESQL_REROUTED_PORT)
@click.option("--username", type=click.STRING)
@click.option("--password", type=click.STRING)
@click.option("--download-directory", type=click.Path(file_okay=False, dir_okay=True))
@click.pass_context
def download(ctx, username, password, database, host, port, download_directory):
    ctx.ensure_object(dict)
    params = DownloadParams(
        username, password, database, host, port, download_directory
    )
    ctx.obj["SQL_ENGINE"] = connect_to_database(params)
    ctx.obj["DOWNLOAD_DIRECTORY"] = params.download_directory


# ----------- DOWNLOAD COMMAND ----------- #
# ----------- TABLE SUBCOMMAND ----------- #
@download.command("table")
@click.option(
    "--table",
    type=click.STRING,
    default="",
    show_default=False,
    help="Name of the table to download",
)
@click.pass_context
def download_tables(ctx, table):
    engine = ctx.obj["SQL_ENGINE"]
    download_directory = ctx.obj["DOWNLOAD_DIRECTORY"]
    DownloadTable(
        engine=engine, table_name=table, download_directory=download_directory
    )


# ----------- DOWNLOAD COMMAND ----------- #
# ---------- COLUMNS SUBCOMMAND ---------- #
@download.command("columns")
@click.option(
    "--table",
    type=click.STRING,
    default="",
    show_default=False,
    help="Name of the table to download",
)
@click.pass_context
def download_select_columns(ctx, table):
    engine = ctx.obj["SQL_ENGINE"]
    download_directory = ctx.obj["DOWNLOAD_DIRECTORY"]
    DownloadColumns(
        engine=engine, table_name=table, download_directory=download_directory
    )


if __name__ == "__main__":
    cli()
