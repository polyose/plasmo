from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

from desmata.lower_protocols import CellContext, DirHasher


class Dependency(BaseModel, ABC):
    id: str
    hash: str
    root: Path
    closure: list['Dependency']

    @staticmethod
    @abstractmethod
    def build_or_get(context: CellContext, hasher: DirHasher) -> 'Dependency':
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
