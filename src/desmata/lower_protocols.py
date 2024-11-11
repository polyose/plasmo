"a protocol is a 'lower' protocol if it does not depend on desmata.interfaces"
import logging
from collections.abc import Callable
from enum import StrEnum, auto
from pathlib import Path
from typing import Protocol, TypeAlias, runtime_checkable

from sqlalchemy.engine import Engine

class LogSubject(StrEnum):
    proc = auto()
    msg = auto()


@runtime_checkable
class Loggers(Protocol):
    proc: logging.Logger
    msg: logging.Logger

    def get(self, subject: LogSubject):
        pass

    def specialize(self, name: str) -> "Loggers":
        pass


EnvVars: TypeAlias = dict[str, str]
EnvFilter: TypeAlias = Callable[[EnvVars], EnvVars]

LogMatcher: TypeAlias = Callable[[...], bool]
LogCallback: TypeAlias = Callable[[...], None]


@runtime_checkable
class LogListener(Protocol):
    def register(
        self, key: str, subject: LogSubject, matcher: LogMatcher, callback: LogCallback
    ):
        pass

    def unregister(self, key: str):
        pass


class Caller(Protocol):
    node: str
    user: str
    platform: str
    pid: int


class CellContext(Protocol):
    name: str
    caller: Caller
    cell_dir: Path
    home: Path
    loggers: Loggers

    def get_env_filter(
        self,
        *,
        exec_path: Path | list[Path],
        passthru_vars: list[str],
        set_default_env: bool,
        env_overrides: EnvVars,
    ) -> EnvFilter:
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


