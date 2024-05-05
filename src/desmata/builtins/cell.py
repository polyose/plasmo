from logging import Logger
from pathlib import Path

from desmata.interface import Cell, Closure, Dependency
from desmata.nix import Nix
from desmata.tool import Tool


class Dependencies(Closure):
    class IPFS(Dependency):
        @staticmethod
        def ensure_path(nix: Nix) -> Path:
            return nix.build("ipfs", "/bin/ipfs")

    class Git(Dependency):
        @staticmethod
        def ensure_path(nix: Nix) -> Path:
            return nix.build("git", "/bin/git")

    ipfs: "Dependencies.IPFS"
    git: "Dependencies.Git"


class IPFS(Tool):
    def __init__(self, closure: Dependencies, log: Logger):
        super().__init__(name="ipfs", path=closure.ipfs.path, log=log)

    def hash(self, target: Path) -> str:
        output = self("ipfs", "add", "-r", "--only-hash", str(target.resolve()))
        # sample output:
        #   added QmWfbz6Tvds3X2y3iUv994ootBQ8JdyspiEqYXtAVHPfVB builtins/flake.lock
        #   added QmcA67vzYhWSCBB3KKFFtTbyVxy349SRQpzUF4Be8r4hft builtins/flake.nix
        #   added QmS2CjUTboH59Pfz2BwRFJpBbQboAiqQvyoq3wPF9e9Wwf builtins
        # Take the last hash, which will be the toplevel dir
        # (or just the file if the target wasn't a dir)
        return output.splitlines()[-1].split()[1]


class Git(Tool):
    def __init__(self, closure: Dependencies, log: Logger):
        super().__init__(name="git", path=closure.git.path, log=log)


class DesmataBuiltins(Cell):
    ipfs: IPFS
    git: Git

    def __init__(self, closure: Dependencies, log: Logger):
        super().__init__(closure)
        self.ipfs = IPFS(closure, log=log)
        self.git = Git(closure, log=log)
