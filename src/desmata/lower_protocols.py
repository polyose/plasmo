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

class PathAdder(Protocol):
    def add(path: Path) -> Path:
        """
        Builders might put files anywhere, use an adder to bring them under desmata control.
        This ensures that if they're deleted by the builder, desmata still has them.
        """
        pass


