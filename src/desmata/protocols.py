import logging
from typing import Protocol, runtime_checkable, TypeVar
from desmata.interface import Cell

from pathlib import Path
from sqlalchemy.engine import Engine


@runtime_checkable
class Loggers(Protocol):
    proc: logging.Logger
    msg: logging.Logger

    def specialize(self, name: str) -> 'Loggers':
        pass


class CellContext(Protocol):
    cell_dir: Path
    home: Path
    loggers: Loggers

    def env(self, dependency_dirs: Path | list[Path] = []) -> dict[str, str]:
        """
        Cell tools might not inherit env vars from the surrounding environment,
        instead they get this env.  This allows cells to encapsulate their dependencies
        properly rather than depending on data from places in the user's environment
        which desmata does not control.
        """
        pass

@runtime_checkable
class UserspaceFiles(Protocol):
    home: Path
    config: Path
    cache: Path
    data: Path
    state: Path

@runtime_checkable
class DBFactory(Protocol):

    def get_engine(self) -> Engine:
        "creates a db if it doesn't exist"
        pass

    def delete_db(self) -> None:
        pass

SpecificCell = TypeVar("SpecificCell", bound=Cell)

@runtime_checkable
class CellFactory(Protocol):

    
    def get(CellType: type[SpecificCell]) -> SpecificCell:
        pass

