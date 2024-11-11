"a protocol is a 'higher' protocol if it depends on something in desmata.interfaces"
from typing import Protocol, TypeAlias, TypeVar, runtime_checkable

from desmata.interface import Cell, Closure, Dependency

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



class DesmataHasher(Protocol):

    def get_dependency_hash(self, dep: Dependency) -> DependencyHash:
        raise NotImplementedError()

    def get_cell_hash(self, closure: Closure) -> CellHash:
        raise NotImplementedError()

    def get_nucleus_hash(self, closure: Closure) -> NucleusHash:
        raise NotImplementedError()

