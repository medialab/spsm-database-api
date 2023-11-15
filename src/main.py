import click
import duckdb

from src.connect import connect_to_database
from src.constants import (
    POSTGRESQL_DB_NAME,
    POSTGRESQL_REROUTED_HOST,
    POSTGRESQL_REROUTED_PORT,
)
from src.download_table import download_table


@click.group()
def cli():
    pass


@cli.group()
@click.option("--database", default=POSTGRESQL_DB_NAME)
@click.option("--host", default=POSTGRESQL_REROUTED_HOST)
@click.option("--port", default=POSTGRESQL_REROUTED_PORT)
@click.option("--username", prompt=True, hide_input=False, type=click.STRING)
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    default="",
    show_default=False,
    type=str,
)
@click.pass_context
def remote(ctx, username, password, database, host, port):
    ctx.ensure_object(dict)
    ctx.obj["POSTGRES_CONNECTION"] = connect_to_database(
        username, password, database, port, host
    )


@remote.command("download-tables")
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


@cli.group("local")
@click.option(
    "--database",
    prompt="""
Path to the local DuckDB database. If you want to
process everything in memory, without creating a,
file, press enter for the default path ':memory:'.
    """,
    type=str,
    default=":memory:",
    show_default=True,
)
@click.pass_context
def local(ctx, database):
    ctx.ensure_object(dict)
    connection = duckdb.connect(database)
    ctx.obj["DUCKDB_CONNECTION"] = connection


@local.command()
@click.pass_context
def query(ctx):
    pass


if __name__ == "__main__":
    cli()
