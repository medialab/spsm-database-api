from typing import Dict

import psycopg2
import psycopg2.extensions
from psycopg2 import OperationalError
from psycopg2.extensions import connection as Connection


def connect_to_database(yaml: Dict, username: str) -> Connection:
    config = yaml["connection"]
    port = config["db_port"]

    try:
        connection = psycopg2.connect(
            database=config["db_name"],
            user=username,
            password=config["db_password"],
            host=config["db_host"],
            port=config["db_port"],
        )
        print(f"\nConnection to PostgreSQL DB at port {port} successful :)\n")
    except OperationalError as e:
        print(f"\nThe error {e} occured.\nConnection at port {port} failed.")
        raise e
    return connection
