def write_template(database: str):
    if not database:
        database = ":memory:"
    return {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "id": "b3778771-779f-4000-8106-26ad5af4f595",
                "metadata": {},
                "outputs": [],
                "source": ["import duckdb"],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "id": "43f7e558-cf45-4a1f-b177-bb4b5c9c49f2",
                "metadata": {},
                "outputs": [],
                "source": ['db_connection = duckdb.connect("{}")'.format(database)],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "id": "0c5973b2-72e1-4165-9a7a-8b3cbfdbf7b3",
                "metadata": {},
                "outputs": [],
                "source": ['db_connection.execute("show tables").fetchall()'],
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.11.4",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
