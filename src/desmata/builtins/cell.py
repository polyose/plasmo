from pathlib import Path

from desmata.cell_utils import get_nix
from desmata.higher_protocols import (
    CellHash,
    CellHashes,
    DependencyHash,
    Hasher,
    NucleusHash,
    Storage,
)
from desmata.interface import Cell, Closure, Dependency
from desmata.lower_protocols import CellContext, DirHasher
from desmata.higher_protocols import ProtoDependency
from desmata.tool import Tool


class Tools:
    class SQLite(Tool):
        def __init__(self, root: Path, context: CellContext):
            loggers = context.loggers.specialize("sqlite")
            sqlite_path_entry = root / "bin"
            sqlite_exe = sqlite_path_entry / "sqlite3"
            super().__init__(
                name="sqlite",
                path=sqlite_exe,
                log=loggers.proc,
                env_filter=context.get_env_filter(exec_path=sqlite_path_entry),
            )
        

    class IPFS(Tool, DirHasher):
        def __init__(self, root: Path, context: CellContext):
            loggers = context.loggers.specialize("ipfs")
            ipfs_path_entry = root / "bin"
            ipfs_exe = ipfs_path_entry / "ipfs"
            super().__init__(
                name="ipfs",
                path=ipfs_exe,
                log=loggers.proc,
                env_filter=context.get_env_filter(exec_path=ipfs_path_entry),
            )

        def get_hash(self, target: Path) -> str:
            output = self("add", "-r", "--only-hash", str(target.resolve()))
            # sample output:
            #   added QmWfbz6Tvds3X2y3iUv994ootBQ8JdyspiEqYXtAVHPfVB builtins/flake.lock
            #   added QmcA67vzYhWSCBB3KKFFtTbyVxy349SRQpzUF4Be8r4hft builtins/flake.nix
            #   added QmS2CjUTboH59Pfz2BwRFJpBbQboAiqQvyoq3wPF9e9Wwf builtins
            # Take the last hash, which will be the toplevel dir
            # (or just the file if the target wasn't a dir)
            return output.splitlines()[-1].split()[1]


class Deps:
    class IPFS(Dependency):
        @staticmethod
        def build_or_get(context: CellContext, hasher: DirHasher) -> "Deps.IPFS":
            nix = get_nix(context)

            # get files
            add = context.dep_adder(None, None) # todo: populate these

            _root, _deps = nix.build("ipfs")
            for tree in nix.grow_trees(_root, _deps):
                dep = add(ProtoDependency(path=tree.info.path, deps )


            root = context.situate(_root.path)
            deps = map(context.situate, (x.path for x in _deps))


            # use ipfs to hash ipfs
            ipfs_tool = Tools.IPFS(root=root.path, context=context)
            ipfs_tool("init")

            hash = ipfs_tool.get_hash(root)
            id = Dependency.get_id(root)
            return Deps.IPFS(id=id, hash=hash, root=root, closure=transitive_deps)

    class Git(Dependency):
        @staticmethod
        def build_or_get(context: CellContext, hasher: DirHasher) -> "Deps.IPFS":
            nix = get_nix(context)
            root, transitive_deps = nix.build("git")
            hash = hasher.get_hash(root)
            id = Dependency.get_id(root)
            return Deps.Git(id=id, hash=hash, root=root, closure=transitive_deps)


class BuiltinsClosure(Closure):
    ipfs: Deps.IPFS
    git: Deps.Git


class DesmataBuiltins(Cell[BuiltinsClosure], Hasher, Storage):
    ipfs: Tools.IPFS

    def __init__(self, closure: BuiltinsClosure, context: CellContext):
        self.ipfs = closure.ipfs.get_tool(context)

    def get_dependency_hash(self, dep: Dependency) -> DependencyHash:
        raise NotImplementedError()

    def get_cell_hash(self, closure: Closure) -> CellHash:
        raise NotImplementedError()

    def get_nucleus_hash(self, closure: Closure) -> NucleusHash:
        raise NotImplementedError()

    def pack_cell(self, closure: Closure) -> CellHashes:
        raise NotImplementedError()

    def unpack_cell(self, hash: CellHash, into: Path) -> CellHashes:
        raise NotImplementedError()
