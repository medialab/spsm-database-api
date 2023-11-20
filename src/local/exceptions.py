from typing import Set


class MissingRelationReferencedInQuery(Exception):
    """Relations referenced in the query were not provided in the tables option."""

    def __init__(self, relations: Set) -> None:
        missing = ", ".join([f"'{r}'" for r in relations])
        msg = "NO FILE PROVIDED FOR: " + missing
        super().__init__(msg)
