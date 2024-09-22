from pathlib import Path

from desmata.protocols import CellContext
from desmata.interface import Cell, Closure, Dependency, Hasher

from desmata.tool import Tool
from desmata.cell_utils import get_nix


class Tools:
    class IPFS(Tool, Hasher):
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
        def build_or_get(context: CellContext, hasher: Hasher) -> "Deps.IPFS":
            nix = get_nix(context)

            # get files
            root = nix.build("ipfs")

            # use ipfs to hash ipfs
            ipfs_tool = Tools.IPFS(root=root, context=context)
            ipfs_tool("init")

            hash = ipfs_tool.get_hash(root)
            id = Dependency.get_id(root)
            return Deps.IPFS(id=id, hash=hash, root=root)

    class Git(Dependency):
        @staticmethod
        def build_or_get(context: CellContext, hasher: Hasher) -> "Deps.IPFS":
            nix = get_nix(context)
            root = nix.build("git")
            hash = hasher.get_hash(root)
            id = Dependency.get_id(root)
            return Deps.Git(id=id, hash=hash, root=root)


class BuiltinsClosure(Closure):
    ipfs: Deps.IPFS
    git: Deps.Git


class DesmataBuiltins(Cell[BuiltinsClosure]):
    ipfs: Tools.IPFS

    def __init__(self, closure: BuiltinsClosure, context: CellContext):
        self.ipfs = closure.ipfs.get_tool(context)
