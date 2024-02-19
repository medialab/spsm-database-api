# SPSM Database API

Command-line tool for downloading data from the SPSM project's PostgreSQL database server.

## Table of contents

- [Installation](#install-the-tool)
- [Downloading from remote database](#download-data)

## Install the tool

1. Create a virtual Python environment with version 3.11 of Python.
2. Activate the environment.
3. With the environment activated, install this tool using the following command:

```shell
pip install git+https://github.com/medialab/spsm-database-api.git
```

4. Test your installation with the following command:

```console
$ spsm --help
```

## Download data

For downloading data from the project's secure PostgreSQL server, you'll need two things:

1. A terminal running in the background, in which the remote PostgreSQL server's port is being rerouted to your computer's port 54321.
2. A user profile on the server, which has been granted permissions to select from tables.

Start downloading with `spsm download`. After which, the terminal will prompt you to enter information necessary for all data downloads.

```
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ Parameter ┃ User input        ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ Database  │ spsm-database     │
│ Host      │ localhost         │
│ Port      │ 54321             │
│ Username  │ firstname.lastname│
│ Password  │                   │
└───────────┴───────────────────┘
───────────── Connected to the PostgreSQL database ──────────────
```

If you don't want to be prompted, you can enter the information directly as options after `spsm download`.

```
$ spsm download --username 'YOUR.USERNAME' --password YOUR-PASSWORD
```
