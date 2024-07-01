import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Protocol, TypeVar

from pydantic import BaseModel

from desmata.config import CellHome
from desmata.git import Git


class Hasher(Protocol):
    """
    Something that can be given a directory and return a hash of its contents
    """

    def get_hash(self, path: Path) -> str:
        raise NotImplementedError()


class Builder(Protocol):
    """
    Something that will accept a package name e.g.
        nix build somepkg

    ...and create a directory with predictable contents:
        /nix/store/somepkg-1.2.3

    """

    def build(self, package: str) -> Path:
        """
        Given a package name (likely defined in a flake.nix in the cell dir),
        build (or download) it and return the directory where it went.
        """
        raise NotImplementedError()


@dataclass
class Loggers:
    msg: logging.Logger
    proc: logging.Logger


@dataclass
class Bootstraps(Builder, Hasher, Loggers):
    # right now the builder is always nix and the hasher is always IPFS
    # this object uses the protocols below because maybe these things will
    # be configurable in the future
    builder: Builder
    hasher: Hasher
    git: Git
    home: CellHome

    def build(self, package: str) -> Path:
        return self.builder.build(package)

    def hash(self, path: Path) -> str:
        raise self.hasher.hash(path)


class HashableClass:
    class_id: str

    def __init__(self, class_id: str):
        self.class_id = class_id

    def __lt__(self, other: "HashableClass") -> bool:
        return self.class_id < other.class_id

    def __hash__(self) -> int:
        return self.class_id.__hash__()


class Dependency(BaseModel, HashableClass, ABC):
    id: str
    hash: str
    root: Path

    @abstractmethod
    def __init__(self, bootstraps: Bootstraps, home: CellHome) -> None:
        raise NotImplementedError()

    def __post_init__(self):
        HashableClass.__init__(self.home.cell_name)

    @staticmethod
    def get_id(root: Path) -> str:
        if root.parts[:3] != ("/", "nix", "store"):
            raise NotImplementedError(
                f"Unable to determine a suitable dependency ID from {root.resolve()}, "
                "please override get_id(Path) on the corresponding subclass of Dependency"
            )
        else:
            return root.parts[3]


class Closure(BaseModel, HashableClass, ABC):
    local_name: str
    dependencies: list[Dependency]
    hash: str
    nucleus_hash: str

    def __post_init__(self):
        HashableClass.__init__(self.home.cell_name)

    @property
    def dependency_inputs(self) -> list[str]:
        return ["./flake.nix", "./flake.lock"]

    @property
    def nucleus(self) -> list[str]:
        return ["./flake.nix", "./flake.lock"]

    @property
    def membrane(self) -> list[str]:
        return ["./cell.py"]


SpecificClosure = TypeVar("SpecificClosure", bound=Closure)


class Cell(ABC, HashableClass, Generic[SpecificClosure]):
    closure: SpecificClosure

    def __init__(self, closure: Closure):
        self.closure = closure
        HashableClass.__init__()

    @classmethod
    def cell_path(cls) -> str:
        return Path(cls.__file__)

    @classmethod
    def cell_name(cls) -> str:
        # TODO: ensure no naming conflicts exist with previously registered cells
        return Path(cls.__file__).name

    def get_logger(self) -> logging.Logger:
        # todo: add handlers so that `desmata observe` can view cell I/O
        logger = logging.getLogger(f"desmata.{self.closure.local_name}")
        logger.setLevel(logging.DEBUG)
