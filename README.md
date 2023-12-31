# SPSM Database API

Command-line tool for downloading data from the SPSM project's PostgreSQL database server.

It takes advantage of 2 different Database Management Systems (DBMS) to do 2 different types of tasks.

<table>
  <tr>
    <th>Task</th>
    <td>Access</td>
    <td>Analysis</td>
  </tr>
  <tr>
    <th>Solution</th>
    <td><a href="https://www.postgresql.org"><img src="doc/img/postgres.png" alt="postgres" style="height:50px;"/></a></td>
    <td><a href="https://duckdb.org/"><img src="doc/img/duckdb.png" alt="postgres" style="height:40px;"/></a></td>
  </tr>
  <tr>
    <th>Command</th>
    <td><code>spsm download SUBCOMMAND</code></td>
    <td><code>spsm duckdb SUBCOMMAND</code></td>
  </tr>
  <tr>
    <th>Explanation</th>
    <td>PostgreSQL is great at reliably storing data and managing access.</td>
    <td>DuckDB is great at efficiently executing queries. Plus, it's an "embedded" DBMS, so while working with it on your computer (rather than a server) you can easily join / introduce other CSV files you have locally on your computer.</td>
  </tr>
</table>

## Table of contents

- [Installation](#install-the-tool)
- [Downloading from remote database](#download-data)
  - [Download an entire table](#download-an-entire-table)
  - [Download part of a table](#download-select-columns-from-a-table)
- [Working with data locally](#local-duckdb-database-for-analysis)
  - [Execute SQL file](#execute-sql-file)
  - [Experiment in Notebook](#launch-jupyter-notebook)

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

## Download data

For downloading data from the project's secure PostgreSQL server, you'll need two things:

1. A terminal running in the background, in which the remote PostgreSQL server's port is being rerouted to your computer's port 54321.
2. A user profile on the server, which has been granted permissions to select from tables.

Start downloading with `spsm download SUBCOMMAND`. After which, the terminal will prompt you to enter information necessary for all data downloads.

![download command](doc/img/download.gif)

If you don't want to be prompted, you can enter the information directly as options after `spsm download`.

```
$ spsm download --username 'YOUR.USERNAME' --password YOUR-PASSWORD --download-directory /PATH/TO/FILE.csv SUBCOMMAND
```

### Download an entire table

To download an entire table onto your computer and/or disk, run the following command:

```console
$ spsm download table
```

As described above, the terminal will prompt you to enter the information necessary for all types of data download.

Then you will be prompted to enter the name of the table you want to download.

![download table](doc/img/download_table.png)

If you don't want to be prompted, you can enter the information with options.

```console
$ spsm download --username 'YOUR.USERNAME' --password YOUR-PASSWORD --download-directory /PATH/TO/FILE.csv table --table TABLE_NAME
```

### Download select columns from a table

To download only certain columns of a table, which might be a good idea if it has text columns and the file would otherwise be very big, run the following command:

```console
$ spsm download columns
```

First, as in the [`spsm download table`](#download-an-entire-table) command, the terminal will prompt you to enter the name of the table you want to download.

Then, you'll be asked to begin entering the columns you want to download.

![download columns](doc/img/download_columns.gif)

## Local DuckDB database (for analysis)

[DuckDB](https://duckdb.org/) is another Database Management System (DBMS), different from PostgreSQL. Whereas PostgreSQL is great for reliably storing data and managing access, DuckDB is excellent at efficiently executing queries. DuckDB is [faster](https://duckdb.org/why_duckdb.html#fast-analytical-queries) than most other Database Management Systems, including PostgreSQL.

### TPC-H benchmark <sup>1</sup>

| query | duckdb (sec) | postgres (sec) |
| ----- | ------------ | -------------- |
| 1     | 0.03         | 1.12           |
| 2     | 0.01         | 0.18           |
| 3     | 0.02         | 0.21           |
| 4     | 0.03         | 0.11           |
| 5     | 0.02         | 0.13           |
| 6     | 0.01         | 0.21           |
| 7     | 0.04         | 0.20           |
| 8     | 0.02         | 0.18           |
| 9     | 0.05         | 0.61           |
| 10    | 0.04         | 0.35           |
| 11    | 0.01         | 0.07           |
| 12    | 0.01         | 0.36           |
| 13    | 0.04         | 0.32           |
| 14    | 0.01         | 0.21           |
| 15    | 0.03         | 0.46           |
| 16    | 0.03         | 0.12           |
| 17    | 0.05         | > 60.00        |
| 18    | 0.08         | 1.05           |
| 19    | 0.03         | 0.31           |
| 20    | 0.05         | > 60.00        |
| 21    | 0.09         | 0.35           |
| 22    | 0.03         | 0.15           |

<sup>1</sup> [Hannes Mühleisen (2022)](https://duckdb.org/2022/09/30/postgres-scanner.html)

Furthermore, contrary to PostgreSQL, DuckDB is what's called an "in-process" DBMS and does not require a server. Everything is immediately accessible in a single file. (An example file name, if you want to save a database with the tables you create / import from CSV files, is `spsm.db`.)

For these reasons, DuckDB is a great solution for locally working with tables you have previously downloaded from the remote database--and joining with CSV files you have on your computer. The only drawback is ensuring the tables you're working with locally are up to date with what's on the PostgreSQL server, but that's less of an issue in the SPSM project.

### Execute SQL file

To execute the query saved in an SQL file, call the `query` subcommand.

```console
$ spsm duckdb query
```

First, the terminal will ask if you want to save the database to a file, which will preserve data imports for later use. If you do not want to create a database file, DuckDB will process everything in-memory.

Then, the terminal will prompt you to provide the paths to (a) the SQL file in which your query is saved and (b) the CSV file in which you want to export the result.

Once the program reads the provided SQL query, it will search for the referenced tables (relations) in the DuckDB database. If it doesn't find them, you will be prompted to provide the paths to CSV files that contain this information.

If you don't want to be prompted, you can provide the relations' names and their data files directly as options after the command.

```console
$ spsm duckdb --database ":memory:" query --query query.sql  --outfile output.csv --table claims downloads/claims.csv --table dataset_de_facto downloads/dataset_de_facto.csv
```

In the example below, you see that (1) we are working with a new, in-memory DuckDB database, which has no prior tables, and (2) the provided SQL query requires the tables `claims` and `dataset_de_facto`. Using the commands above (i.e. [`spsm download table`](#download-data)), we have these referenced tables saved in a folder named `./downloads`. The example shows how, having parsed the query in the provided SQL file (`./query.sql`), the program sequentially asks us to provide these files and then proceeds to create tables in the in-memory database containing their rows and columns. Finally, after preparing the database, the program executes the query and writes the result to the given out-file (`./output.csv`).

![duckdb execute sql file](doc/img/execute_query.gif)

### Launch Jupyter notebook

To experiment with SQL queries, run `spsm duckdb notebook` and launch a Jupyter notebook.

```console
$ spsm duckdb notebook
```

To provide access to relevant files, including CSV files and/or a DuckDB file, you should provide the path to a directory. If you don't provide a path, the notebook's workspace will be launched from wherever you run the command. Finally, if the directory from which the notebook is launched doesn't already have a Jupyter notebook file, one will be created using the same database configuration provided with all `spsm duckdb` commands, as described above. If the directory already has a Jupyter notebook but you want to create a new one anyway, provide a path with the option "--new".

```console
$ spsm duckdb --database './spsm.db' notebook --new 'Notebook.ipynb'
```

The above command would create a notebook in the current working directory, meaning the location from which the command is run. And it relies on an existant DuckDB database file in the same directory.

```console
./
 |__ Notebook.ipynb
 |__ spsm.db
 |__ downloads/
    |__ claims.csv
    |__ selection_tweet.csv
    |__ tweet_claim.csv
```

With the database configuration declared in the parent `spsm duckdb` command, the subcommand `spsm duckdb notebook` launches a Jupyter notebook with code blocks establishing a DuckDB connection already written in the notebook.
