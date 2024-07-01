from sqlmodel import (
    Field,
    SQLModel,
    Relationship,
)
from pathlib import Path
from sqlalchemy.types import VARCHAR, TypeDecorator

class PathType(TypeDecorator):
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if isinstance(value, Path):
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return Path(value)
        return value

class Cell(SQLModel, table=True):
    name: Field(str, primary_key=True)
    workspace_sites: list["Site"] = Relationship(back_populates="cell")

class Site(SQLModel, table=True):
    path: Field(Path, primary_key=True, sa_column=PathType())
    cell_name: Field(str, foreign_key="cell.name")
    mutable: bool = Field(default=False)
    cell: Cell = Relationship(back_populates="workspace_sites")



