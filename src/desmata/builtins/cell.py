from logging import Logger
from pathlib import Path

from desmata.config import CellHome
from desmata.interface import cell, Cell, Closure, Dependency, Builder, Loggers
from desmata.tool import Tool
from desmata.nix import Nix


class IPFS(Tool, Dependency):
    @staticmethod
    def build_or_get(builder: Nix, home: CellHome, loggers: Loggers) -> 'IPFS':

        # get files
        root = builder.build("ipfs")
        id = Dependency.get_id(root)
        ipfs = IPFS(id=id, root=root, hash='pending')

        # prep for use a tool
        ipfs.prepare(home, loggers)
        ipfs("init")

        # calculate pending hash
        ipfs.hash = ipfs.get_hash(ipfs.root)
        return ipfs

    def prepare(self, home: CellHome, loggers: Loggers):
        binary = self.root / "bin/ipfs"

        Tool.__init__(
            name="ipfs",
            path=binary,
            # don't inherit env vars
            env_filter=lambda _: home.env([binary]),
            log=loggers.proc,
        )

    def get_hash(self, target: Path) -> str:
        output = self("ipfs", "add", "-r", "--only-hash", str(target.resolve()))
        # sample output:
        #   added QmWfbz6Tvds3X2y3iUv994ootBQ8JdyspiEqYXtAVHPfVB builtins/flake.lock
        #   added QmcA67vzYhWSCBB3KKFFtTbyVxy349SRQpzUF4Be8r4hft builtins/flake.nix
        #   added QmS2CjUTboH59Pfz2BwRFJpBbQboAiqQvyoq3wPF9e9Wwf builtins
        # Take the last hash, which will be the toplevel dir
        # (or just the file if the target wasn't a dir)
        return output.splitlines()[-1].split()[1]


class Git(Tool):
    def __init__(self, builder: Builder, log: Logger):
        super().__init__(name="git", path=closure.git.path, log=log)


class BuiltinsClosure(Closure):
    ipfs: IPFS
    git: Git


@cell(Closure=BuiltinsClosure)
class DesmataBuiltins(Cell[BuiltinsClosure]):
    ipfs: IPFS
    git: Git

    def __init__(self, closure: BuiltinsClosure):
        self.ipfs = IPFS(closure)
        self.git = Git(closure)
