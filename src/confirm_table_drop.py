from rich.align import Align
from rich.console import Console
from rich.prompt import Confirm
from rich.text import Text
from sqlalchemy import Engine, MetaData, inspect
from sqlalchemy.orm import declarative_base


def drop_table(table_name: str, engine: Engine) -> None:
    metadata = MetaData()
    MetaData.reflect(metadata, bind=engine)
    TABLE = metadata.tables[table_name]

    if TABLE is not None:
        base = declarative_base()
        try:
            base.metadata.drop_all(engine, [TABLE], checkfirst=True)
        except Exception as e:
            raise e
    else:
        raise ValueError("table is None")

    if table_name in inspect(engine).get_table_names():
        raise RuntimeError("Table was not deleted")


def confirm_table_deletion(console: Console, engine: Engine, table_name: str) -> bool:
    """Code triggered if the user input a table name that already exists."""

    delete_the_table = Confirm.ask(
        "\nAssuming you have permission, do you want to delete this table?"
    )

    if not delete_the_table:
        return False

    else:
        console.clear()

        # Remind the user about what they're doing
        text = Align.left(
            Text(
                f"You are about to delete the table '{table_name}'.",
            ),
        )
        console.print(text, style="white on red")
        text = Align.left(
            Text(
                "\nAs a reminder, these are the tables in the database:\n{}".format(
                    inspect(engine).get_table_names()
                ),
            ),
        )
        console.print(text, style="white on red")

        # Ask the user to confirm a second/final time
        confirmation = Confirm.ask(
            Text(
                f"Are you very sure sure you want to delete the table '{table_name}'?",
                justify="center",
            )
        )

        # If the user really wants to delete the table, delete it
        if confirmation:
            drop_table(table_name=table_name, engine=engine)
            console.print("\n[green]You deleted the table.")
            console.print(
                "Now, these are the tables currently in the database: {}".format(
                    inspect(engine).get_table_names()
                )
            )
            return True
        else:
            return False
