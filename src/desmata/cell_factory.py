import importlib
import os
import platform
import re
from pathlib import Path

from sqlalchemy import Engine

from desmata.builtins.cell import DesmataBuiltins, Tools
from desmata.exceptions import BadCellClassException
from desmata.interface import Closure, Dependency
from desmata.protocols import (
    Caller,
    CellContext,
    CellFactory,
    DBFactory,
    EnvFilter,
    EnvVars,
    Loggers,
    SpecificCell,
    UserspaceFiles,
)

default_passthrough_vars = [
    "TERM",
    "COLORTERM",
    "EDITOR",
    "VISUAL",
    "PAGER",
    "LANG",
    "LC_.*",
]

user = "desmata-user"

# home subdirs
cache = ".cache"
config = ".config"
share = ".local/share"
state = ".local/state"
tmp = ".tmp"
home_subdirs = [cache, config, share, state, tmp]

class LocalCaller(Caller):

    def __init__(self):
        self.node = platform.node()
        self.platform_desc = platform.platform()
        self.user = os.getlogin()
        self.pid = os.getpid()

    node: str
    user: str
    platform: str
    pid: int

class BasicContext(CellContext):
    caller: Caller
    cell_dir: Path
    home: Path
    loggers: Loggers

    def __init__(
            self, name: str, cell_dir: Path, userspace: UserspaceFiles, loggers: Loggers
        ):
            self.cell_dir = cell_dir
            self.caller = LocalCaller()

            self.home = userspace.data / "cells" / name / "home" / "desmata-user"
            for subdir in home_subdirs:
                home_subdir = self.home / subdir
                home_subdir.mkdir(parents=True, exist_ok=True)
            self.loggers = loggers.specialize(name)


    def _get_default_env(self) -> EnvVars:
        return {
            "USER": "desmata-user",
            "HOME": str(self.home), 
            "TMP": str(self.home / tmp), 
            "XDG_CACHE_HOME": str(self.home / cache), 
            "XDG_CONFIG_HOME": str(self.home / config), 
            "XDG_DATA_HOME": str(self.home / share),
            "XDG_STATE_HOME": str(self.home / state),
        }
    
    def _get_passed_thru_vars(self, passthru_vars: list[str]) -> EnvVars:
        """
        Called by the env filter, this passes external vars to the eventual subprocess,
        but only if they're on the list.
        """
        env: EnvVars = {}
        for var, val in os.environ.items():
            for passthru_var in passthru_vars:
                if re.match(passthru_var, var):
                    env[passthru_var] = val
        return env

    def get_env_filter(
        self,
        exec_path: Path | list[Path] = [],
        passthru_vars: list[str] = default_passthrough_vars,
        set_default_env: bool = True,
        env_overrides: EnvVars = {},
    ) -> EnvFilter:

        passthru = self._get_passed_thru_vars(passthru_vars)
        env_vars = self._get_default_env() if set_default_env else {}

        match exec_path:
            case Path():
                deps = str(exec_path)
            case list():
                deps = list(map(str, exec_path))


        def filter(env: EnvVars) -> EnvVars:
            inner_env = env_vars.copy()
            inner_env.update(self._get_passed_thru_vars(passthru))
            if exec_path := inner_env.get("PATH"):
                exec_path = ":".join([*exec_path.split(":"), *deps])
            return inner_env

        return filter


class DefaultCellFactory(CellFactory):
    userspace: UserspaceFiles
    db_factory: DBFactory
    _engine: Engine | None = None

    def __init__(self, log: Loggers, userspace: UserspaceFiles, db_factory: DBFactory):
        self.log = log
        self.userspace = userspace
        self.db_factory = db_factory

    @property
    def engine(self) -> Engine:
        if not self._engine:
            self._engine = self.db_factory.get_engine()
        return self._engine

    def _pick_name(self, candidates: list[str]):
        choice = candidates[0]
        self.log.msg.debug(
            f"TODO: pick from among name candidates {candidates} to avoid collisions"
            f"\nfor now, defaulting to {choice}"
        )
        return choice

    def _cell_name(self, cell_class_file: Path) -> str:
        parts = cell_class_file.parent.parts  # /foo/bar/baz/cell.py
        name_candidates = [
            "/".join(parts[-1 * i :]) for i in range(1, len(parts))
        ]  # ["baz", "bar/baz", "foo/bar/baz"]
        self.log.msg.debug(f"Cell name candidates: {name_candidates}")
        return self._pick_name(name_candidates)

    def _cell_file_inode_device(self, cell_class_file: Path) -> tuple[int, int]:
        stat_info = os.stat(str(cell_class_file))
        return (stat_info.st_ino, stat_info.st_dev)

    @staticmethod
    def _get_closure_type(CellType: type[SpecificCell]) -> type[Closure]:
        closure_types = []
        for base in CellType.__orig_bases__:
            for arg in base.__args__:
                if issubclass(arg, Closure):
                    closure_types.append(arg)

        if len(closure_types) != 1:
            raise BadCellClassException(
                f"Expected exactly one closure type for "
                f"cell type {CellType}, instead got {closure_types}. "
                "Cells should have Cell[SomeClosure] as a base class, "
                "where SomeClosure has Closure as a base class"
            )
        return closure_types[0]

    @staticmethod
    def _get_dependency_types(ClosureType: type[Closure]) -> dict[str, Dependency]:
        dependency_types: dict[str, Dependency] = {}
        print("got:", ClosureType)
        for attr, annotated_type in ClosureType.__annotations__.items():
            if issubclass(annotated_type, Dependency):
                dependency_types[attr] = annotated_type
        return dependency_types

    def get(self, CellType: type[SpecificCell]) -> SpecificCell:
        module_name = CellType.__module__
        module = importlib.import_module(module_name)
        cell_file = Path(module.__file__)
        name = self._cell_name(cell_file)
        inode, device_id = self._cell_file_inode_device(cell_file)
        context = BasicContext(
            name=name,
            cell_dir=cell_file.parent,
            userspace=self.userspace,
            loggers=self.log,
        )
        self.log.msg.debug(f"CONTEXT, {context.__dict__}")

        ClosureType = DefaultCellFactory._get_closure_type(CellType)
        dependency_types = DefaultCellFactory._get_dependency_types(ClosureType)
        dependencies = {
            k: v.build_or_get(context) for k, v in dependency_types.items()
        }  # closure = ClosureType(name=name, ...)

        # get a hasher
        ipfs: Tools.IPFS
        if CellType is DesmataBuiltins:
            ipfs = Tools.IPFS(root=dependencies["ipfs"].root, context=context)
        else:
            ipfs = self.get(DesmataBuiltins).ipfs

        closure = ClosureType(local_name=name, hash="pending", nucleus_hash="pending", **dependencies)
        # calculate the hashes
