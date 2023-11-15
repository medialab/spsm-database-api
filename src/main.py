import click

from src.connect import connect_to_database
from src.constants import (
    POSTGRESQL_DB_NAME,
    POSTGRESQL_REROUTED_HOST,
    POSTGRESQL_REROUTED_PORT,
)
from src.download_table import download_table


@click.group()
@click.option("--database", default=POSTGRESQL_DB_NAME)
@click.option("--host", default=POSTGRESQL_REROUTED_HOST)
@click.option("--port", default=POSTGRESQL_REROUTED_PORT)
@click.option("--username", prompt=True, hide_input=False, type=click.STRING)
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    default="",
    type=str,
)
@click.pass_context
def cli(ctx, username, password, database, host, port):
    ctx.ensure_object(dict)
    ctx.obj["POSTGRES_CONNECTION"] = connect_to_database(
        username, password, database, port, host
    )


@cli.command("download-tables")
@click.pass_context
@click.option(
    "--table", prompt=True, type=click.STRING, help="Name of the table to download"
)
@click.option(
    "--download-directory",
    prompt=True,
    type=click.Path(dir_okay=True, file_okay=False),
    help="Path to the directory in which you want to download the compressed table",
)
def download_tables(ctx, table, download_directory):
    connection = ctx.obj["POSTGRES_CONNECTION"]
    download_table(
        connection=connection, table=table, download_directory=download_directory
    )


@cli.command("export-selection")
@click.pass_context
@click.argument("query")
def query(ctx, query):
    connection = ctx.obj["POSTGRES_CONNECTION"]


if __name__ == "__main__":
    cli(obj={})
