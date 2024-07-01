from pathlib import Path
from typing import TypeVar
import logging
from desmata.nix import Nix
from desmata.interface import Cell, Closure, Dependency, Builder, Hasher, Bootstraps, Loggers
from desmata.builtins.cell import DesmataBuiltins, BuiltinsClosure, IPFS, Git
from desmata.tool import Tool
from desmata.config import CellHome

from dataclasses import dataclass
from functools import cache

SpecificDependency = TypeVar("SpecificDependency", bound=Dependency)
SpecificClosure = TypeVar("SpecificClosure", bound=Closure)
SpecificCell = TypeVar("SpecificCell", bound=Cell)




@cache
def loggers(name: str | None = None) -> Loggers:
    # TODO: handlers and stuff, sensitive to config
    # TODO: use call stack, not module location, to determine logger name

    msg = logging.getLogger("desmata.msg")
    proc = logging.getLogger("desmata.proc")
    if name:
        msg = msg.getChild(name)
        proc = proc.getChild(name)

    msg.setLevel(logging.DEBUG)
    proc.setLevel(logging.DEBUG)

    return Loggers(msg=msg, proc=proc)


@cache
def builder(CellType: type[SpecificCell]) -> Builder:
    # TODO: a builder that only builds if the dependency inputs have changed
    log = loggers("builder")
    return Nix(cwd=Path(CellType.__file__).parent, log=log.subprocess)

@cache
def cell_home(CellType: type[SpecificCell]) -> CellHome:
    return CellHome(CellType.cell_name())


@cache
def hasher(CellType: type[SpecificCell]) -> Hasher:
    return IPFS.build_or_get(builder(DesmataBuiltins), cell_home(DesmataBuiltins), loggers("hasher"))



@cache
def dependency(
    CellType: type[SpecificCell], DepType: type[SpecificDependency]
) -> SpecificDependency:
    straps = bootstraps(CellType)
    path = DepType.ensure_path(straps.nix)
    id = DepType.get_id(path)
    hash = straps.hasher.hash(path)
    cell_home = CellHome(CellType.cell_name())
    return SpecificDependency(id=id, hash=hash, path=path, cell_home=cell_home)


@cache
def closure(
    CellType: type[SpecificCell], ClosureType: type[SpecificClosure]
) -> SpecificCell:
    deps = {}
    for name, Dep in ClosureType.__annotations__.items():
        if issubclass(Dep, Dependency):
            deps[name] = dependency(CellType, Dep)

    hasher = hasher()
    local_name = CellType.cell_name()

    for attr in vars(CellType):
        print(attr)
