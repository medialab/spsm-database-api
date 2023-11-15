import click
import yaml

from src.connect import connect_to_database
from src.download_table import download_table


@click.group()
@click.option("--username", required=False, type=click.STRING)
@click.option(
    "--config", required=False, type=click.Path(file_okay=True, dir_okay=False)
)
@click.pass_context
def cli(ctx, username, config):
    ctx.ensure_object(dict)
    if not username:
        username = click.prompt("Enter your username", type=str)
    if not config:
        config = click.prompt(
            "Enter the path to your configuration YAML file",
            type=click.Path(file_okay=True, dir_okay=False),
        )

    with open(config, "r") as f:
        info = yaml.safe_load(f)
        ctx.obj["POSTGRES_CONNECTION"] = connect_to_database(info, username)


@cli.command("download-tables")
@click.pass_context
@click.option("--table", required=False, type=click.STRING)
@click.option(
    "--download-directory",
    required=False,
    type=click.Path(dir_okay=True, file_okay=False),
)
def download_tables(ctx, table, download_directory):
    connection = ctx.obj["POSTGRES_CONNECTION"]
    if not table:
        table = click.prompt("Enter the name of the table to download", type=str)
    if not download_directory:
        download_directory = click.prompt(
            "Enter the path to the directory in which you want to download the compressed table",
            type=click.Path(file_okay=False, dir_okay=True),
        )

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
