# SPSM Database API

Command-line tool for downloading data from the SPSM project's PostgreSQL database server.

## Table of contents

- [Installation](#install-the-tool)
- [Downloading from remote](#remote-postgresql-database-for-export)
  - [Download tables](#download-tables)
- [Working with data on local database](#local-duckdb-database-for-analysis)

## Install the tool

1. Create a virtual Python environment with version 3.11 of Python.
2. Activate the environment.
3. With the environment activated, install this tool using the following command:

```shell
pip install https://github.com/medialab/spsm-database-api.git
```

4. Test your installation with the following command:

```console
$ spsm --help
```

## Remote PostgreSQL database (for export)

For downloading data from the project's secure PostgreSQL server, you'll need two things:

1. A terminal running in the background, in which the remote PostgreSQL server's port is being rerouted to your computer's port 54321.
2. A user profile on the server, which has been granted permissions to select from tables.

At the start of every command, you'll be prompted to enter the information about connecting to the remote database.

```console
$ spsm remote COMMAND
Username: YOUR.USERNAME
Password: YOUR-PASSWORD

Connection to PostgreSQL DB at port 54321 successful :)
```

If you don't want to be prompted, you can enter them directly as options after `spsm`.

```
$ spsm remote --username 'YOUR.USERNAME' --password YOUR-PASSWORD COMMAND
```

### Download tables

To download an entire table onto your computer and/or disk, run the following command:

```console
$ spsm remote download-tables
```

You will be prompted to enter the name of the table you want to download and the directory in which you want to store the compressed file.

```console
$ spsm remote download-tables
Username: YOUR.USERNAME
Password: YOUR-PASSWORD

Connection to PostgreSQL DB at port 54321 successful :)

Table: claims
Download directory: ./downloads
╭── Downloading ──╮
│ table: 'claims' │
│ size: 193 MB    │
╰─────────────────╯
Downloading... ⠙ 0:00:08

Table downloaded to CSV file 'downloads/claims_2023-11-15.csv.gz'.
```

## Local DuckDB database (for analysis)
