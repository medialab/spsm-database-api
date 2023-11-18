import click
from rich.console import Console
from rich.table import Table


class DownloadParams:
    def __init__(
        self,
        username: str | None,
        password: str | None,
        database: str,
        host: str,
        port: int,
        download_directory: str | None,
    ) -> None:
        self.username = username
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.download_directory = download_directory

        console = Console()
        console.clear()
        table = self.generate_table()
        console.print(table)

        if not self.username:
            self.username = click.prompt(text="Username", hide_input=False, type=str)
        console.clear()
        table = self.generate_table()
        console.print(table)

        if not self.password:
            self.password = click.prompt(
                text="Password", hide_input=True, type=str, default=""
            )
        console.clear()
        table = self.generate_table()
        console.print(table)

        if not self.download_directory:
            self.download_directory = click.prompt(text="Download directory", type=str)
        console.clear()
        table = self.generate_table()
        console.print(table)

    def generate_table(self):
        table = Table()
        table.add_column("[blue]Parameter")
        table.add_column("[green]User input")
        table.add_row("Database", self.database)
        table.add_row("Host", self.host)
        table.add_row("Port", str(self.port))
        table.add_row("Username", self.username)
        if self.password:
            password_string = "*****"
        else:
            password_string = None
        table.add_row("Password", password_string)
        table.add_row("Download directory", self.download_directory)
        return table
