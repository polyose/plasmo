import logging
from typing import Protocol, runtime_checkable
from desmata.interface import Cell

from path import Path
from SQLModel import Engine


class Loggers(Protocol):
    proc: logging.Logger
    msg: logging.Logger

    def specialize(self, name: str) -> None:
        pass


class CellEnv(Protocol):
    home: Path

    def env(self, path: Path | list[Path] = []) -> dict[str, str]:
        """
        Cell tools might not inherit env vars from the surrounding environment,
        instead they get this env.  This helps ensure that cells encapsulate
        their dependencies properly rather than depending on data from suprising
        places in the user's environment.
        """
        pass

@runtime_checkable
class UserspaceFiles(Protocol):
    home: Path
    config: Path
    cache: Path
    data: Path
    state: Path

    def home_for(*, cell_type: type[Cell]) -> Path:
        pass

class DBFactory(Protocol):
    def get_engine(self, userspace: UserspaceFiles) -> Engine:
        pass
