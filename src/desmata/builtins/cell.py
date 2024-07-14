from pathlib import Path

from desmata.protocols import CellEnv, Loggers
from desmata.interface import Cell, Closure, Dependency

from desmata.tool import Tool
from desmata.nix import Nix

class Deps:


    class IPFS(Dependency):

        def get_tool(root: Path, loggers: Loggers, cytosol: CellEnv) -> Tool:
            return Tool(name="ipfs", path=root, log=loggers.proc, env=cytosol.env(path=root / "bin"))

        @staticmethod
        def build_or_get(nix: Nix, cell_env: CellEnv, loggers: Loggers) -> 'Deps.IPFS':

            # get files
            root = nix.build("ipfs")

            # use ipfs to hash ipfs
            ipfs = Deps.IPFS.get_tool(root, loggers)
            ipfs("init")

            ipfs.hash = ipfs.get_hash(root)
            ipfs.id = super().get_id(root)
            return ipfs


        def get_hash(self, target: Path) -> str:
            output = self("ipfs", "add", "-r", "--only-hash", str(target.resolve()))
            # sample output:
            #   added QmWfbz6Tvds3X2y3iUv994ootBQ8JdyspiEqYXtAVHPfVB builtins/flake.lock
            #   added QmcA67vzYhWSCBB3KKFFtTbyVxy349SRQpzUF4Be8r4hft builtins/flake.nix
            #   added QmS2CjUTboH59Pfz2BwRFJpBbQboAiqQvyoq3wPF9e9Wwf builtins
            # Take the last hash, which will be the toplevel dir
            # (or just the file if the target wasn't a dir)
            return output.splitlines()[-1].split()[1]



class BuiltinsClosure(Closure):
    ipfs: Deps.IPFS

class DesmataBuiltins(Cell[BuiltinsClosure]):
    ipfs: Tool

    def __init__(self, closure: BuiltinsClosure, loggers: Loggers, cell_env: CellEnv):
        self.ipfs = closure.ipfs.get_tool(loggers=loggers, cell_env=cell_env)
