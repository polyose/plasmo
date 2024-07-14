from pathlib import Path
from typing import List, Optional

from sqlalchemy import Column
from sqlalchemy.types import VARCHAR, TypeDecorator
from sqlmodel import Field, Relationship, SQLModel


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
    name: str = Field(primary_key=True)
    workspace_sites: List["Site"] = Relationship(back_populates="cell")

    class Config:
        arbitrary_types_allowed = True


class Site(SQLModel, table=True):
    path: Path = Field(sa_column=Column(PathType(), primary_key=True))
    cell_name: Optional[str] = Field(default=None, foreign_key="cell.name")
    mutable: bool = Field(default=False)
    cell: Cell = Relationship(back_populates="workspace_sites")

    class Config:
        arbitrary_types_allowed = True
        
