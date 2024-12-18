"a protocol is a 'higher' protocol if it depends on something in desmata.interfaces"
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import NewType, Protocol, TypeAlias, TypeVar, runtime_checkable

from desmata.lower_protocols import EnvVars, EnvFilter, PathAdder, Caller, Loggers
from desmata.interface import Cell, Closure, Dependency
from desmata.messages import NixPathInfo

SpecificCell = TypeVar("SpecificCell", bound=Cell)

@runtime_checkable
class CellFactory(Protocol):
    def get(CellType: type[SpecificCell]) -> SpecificCell:
        pass

# later on these will have different implementations so they can be made
# to appear differently when shown to the user.

DependencyHash = NewType("DependencyHash", str)
NucleusHash = NewType("NucleusHash", str)
CellHash = NewType("CellHash", str)

@dataclass
class CellHashes:
    cell_hash: CellHash
    nucleus_hash: NucleusHash
    dependency_hashes: dict[str, DependencyHash]


class Hasher(Protocol):

    def get_dependency_hash(self, dep: Dependency) -> DependencyHash:
        raise NotImplementedError()

    def get_cell_hash(self, closure: Closure) -> CellHash:
        raise NotImplementedError()

    def get_nucleus_hash(self, closure: Closure) -> NucleusHash:
        raise NotImplementedError()


class Storage(Protocol):

    def pack_cell(self, closure: Closure) -> CellHashes:
        raise NotImplementedError()

    def unpack_cell(self, hash: CellHash, into: Path) -> CellHashes:
        raise NotImplementedError()

IdGetter : TypeAlias = Callable[[Path], str]
Pathable : TypeAlias = Path | NixPathInfo

@dataclass
class ProtoDependency:
    """
    Dependencies must be added to desmata leaf-first.
    A ProtoDependency has already had its dependencies added, but has not yet been added itself.
    """
    path : Pathable
    deps : list[Dependency]

class CellContext(Protocol):
    name: str
    caller: Caller
    cell_dir: Path
    home: Path
    loggers: Loggers

    def dep_adder(
        self, 
        *, 
        id_getter: Callable[[Path], str], 
        path_adder: PathAdder
    ) -> Callable[[ProtoDependency], Dependency]:
        """
        Gets a function which will takes a local file under desmata's control (via hard links).
        This way if the file changes or is deleted, the version of it which is depended on will remain stable.
        """
        pass

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


