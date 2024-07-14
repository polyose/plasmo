import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Protocol, TypeVar, runtime_checkable

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


class Loggers(Protocol):
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


class Dependency(BaseModel, ABC):
    id: str
    hash: str
    root: Path

    @abstractmethod
    def __init__(self, bootstraps: Bootstraps, home: CellHome) -> None:
        raise NotImplementedError()


    @staticmethod
    def get_id(root: Path) -> str:
        if root.parts[:3] != ("/", "nix", "store"):
            raise NotImplementedError(
                f"Unable to determine a suitable dependency ID from {root.resolve()}, "
                "please override get_id(Path) on the corresponding subclass of Dependency"
            )
        else:
            return root.parts[3]


class Closure(BaseModel, ABC):
    local_name: str
    dependencies: list[Dependency]
    hash: str
    nucleus_hash: str


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


class Cell(ABC, Generic[SpecificClosure]):
    closure: SpecificClosure

    def __init__(self, closure: Closure):
        self.closure = closure
