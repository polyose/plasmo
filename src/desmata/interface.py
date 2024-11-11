from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, Protocol, TypeAlias, TypeVar, runtime_checkable

from pydantic import BaseModel

from desmata.lower_protocols import CellContext, Hasher


class Dependency(BaseModel, ABC):
    id: str
    hash: str
    root: Path
    closure: list[Path]

    @staticmethod
    @abstractmethod
    def build_or_get(context: CellContext, hasher: Hasher) -> 'Dependency':
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
    hash: str
    nucleus_hash: str


    @property
    @staticmethod
    def nucleus() -> list[str]:
        return ["./flake.nix", "./flake.lock"]

    @property
    @staticmethod
    def membrane() -> list[str]:
        return ["./cell.py"]


SpecificClosure = TypeVar("SpecificClosure", bound=Closure)


class Cell(ABC, Generic[SpecificClosure]):
    closure: SpecificClosure

    def __init__(self, closure: Closure):
        self.closure = closure

SpecificCell = TypeVar("SpecificCell", bound=Cell)


@runtime_checkable
class CellFactory(Protocol):
    def get(CellType: type[SpecificCell]) -> SpecificCell:
        pass

# later on these will have different implementations so they can be made
# to appear differently when shown to the user.

DependencyHash: TypeAlias = str
NucleusHash: TypeAlias = str
CellHash: TypeAlias = str


class Hasher(Protocol):

    def get_dependency_hash(self, dep: Dependency) -> DependencyHash:
        raise NotImplementedError()

    def get_cell_hash(self, closure: Closure) -> CellHash:
        raise NotImplementedError()

    def get_nucleus_hash(self, closure: Closure) -> NucleusHash:
        raise NotImplementedError()

class Storage(Protocol):

    def pack_dependency(self, dep: Dependency, hash: DependencyHash):
        raise NotImplementedError()

    def pack_cell(self, closure: Closure, hash: CellHash):
        raise NotImplementedError()

    def unpack_dependency(self, hash: DependencyHash, into: Path):
        raise NotImplementedError()

    def unpack_cell(self, hash: CellHash, into: Path):
        raise NotImplementedError()
