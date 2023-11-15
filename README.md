# SPSM Database API

Command-line tool for downloading data from the SPSM project's PostgreSQL database server.

## Table of contents

1. [Installation](#install-the-tool)
2. [Configuration](#connecting-to-the-database)
3. [Commands](#commands)
   1. [Download tables](#download-tables)

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

## Connecting to the database

All of this tool's commands require accessing the database on the project's secure PostgreSQL server. For this, you'll need two things:

1. A terminal running in the background, in which the remote PostgreSQL server's port is being rerouted to your computer's port 54321.
2. A user profile on the server, which has been granted permissions to select from tables.

At the start of every command, you'll be prompted to enter the information about connecting to the remote database.

```console
$ spsm COMMAND
Username: YOUR.USERNAME
Password: YOUR-PASSWORD

Connection to PostgreSQL DB at port 54321 successful :)
```

If you don't want to be prompted, you can enter them directly as options after `spsm`.

```
$ spsm --username 'YOUR.USERNAME' --password YOUR-PASSWORD COMMAND
```

## Commands

### Download tables

To download an entire table onto your computer and/or disk, run the following command:

```console
$ spsm download-tables
```

You will be prompted to enter the name of the table you want to download and the directory in which you want to store the compressed file.

```console
$ spsm download-tables
Username: YOUR.USERNAME
Password: YOUR-PASSWORD

Connection to PostgreSQL DB at port 54321 successful :)

Table: claims
Download directory: ./downloads

Table: 'claims'
Size: 193 MB

Downloading... ⠏ 0:00:03

Table downloaded to CSV file 'downloads/claims_2023-11-15.csv.gz'.
```
