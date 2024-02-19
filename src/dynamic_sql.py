from typing import Dict

from sqlalchemy import (
    VARCHAR,
    Boolean,
    Column,
    Date,
    DateTime,
    Engine,
    Float,
    Integer,
    Interval,
    MetaData,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, declarative_base


class Base(DeclarativeBase):
    pass


def drop_table(table_name: str, engine: Engine) -> None:
    metadata = MetaData()
    base = declarative_base()
    table = metadata.tables.get(table_name)
    if table is not None:
        base.metadata.drop_all(engine, [table], checkfirst=True)


class ColumnBuilder:
    def __init__(self, primary_key: str) -> None:
        self.pk = primary_key

    def __call__(self, name: str, type_string: str) -> Column:
        return Column(
            self.convert_type(type_string),
            primary_key=self.parse_pk(name),
            autoincrement=False,
        )

    def parse_pk(self, name: str):
        if name == self.pk:
            return True
        else:
            return False

    def convert_type(self, type_string: str):
        if type_string.lower() == "int" or type_string.lower() == "integer":
            return Integer
        elif type_string.lower() == "text":
            return Text
        elif type_string.lower().startswith("varchar"):
            return self.convert_varchar(type_string)
        elif type_string.lower() == "float":
            return Float
        elif type_string.lower() == "bool" or type_string.lower() == "boolean":
            return Boolean
        elif type_string.lower() == "date":
            return Date
        elif type_string.lower() == "datetime":
            return DateTime
        elif type_string.lower() == "interval":
            return Interval
        else:
            return String

    def convert_varchar(self, type_string: str) -> VARCHAR:
        var_length = type_string.split("(")[1].split(")")[0]
        return VARCHAR(int(var_length))


def create_table(table_name: str, primary_key: str, mapping_yaml: Dict):
    schema = {"__tablename__": table_name}
    builder = ColumnBuilder(primary_key=primary_key)

    for colum_name, data_type in mapping_yaml.items():
        # For each column, pair the name with an SQLAlchemy Column object
        schema.update({colum_name: builder(colum_name, data_type)})

    # Return an SQLAlchemy declarative table with the column schema
    return type(table_name, (Base,), schema)
