import psycopg2
import psycopg2.extensions
from psycopg2 import OperationalError
from psycopg2.extensions import connection as Connection


def connect_to_database(
    username: str, password: str, database: str, port: str, host: str
) -> Connection:
    try:
        connection = psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=host,
            port=port,
        )
        print(f"\nConnection to PostgreSQL DB at port {port} successful :)\n")
    except OperationalError as e:
        print(f"\nThe error {e} occured.\nConnection at port {port} failed.")
        raise e
    return connection
