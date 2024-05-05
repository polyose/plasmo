from logging import Logger

from pathlib import Path
from desmata.interface import CellBase, ClosureBase, DependencyBase
from desmata.nix import Nix
from desmata.tool import Tool
from logging import Logger


class Hello(DependencyBase):
    def ensure_path(nix: Nix, log: Logger) -> Path:
        nix.build(
            # a package name, refers to flake.nix's outputs
            "hello",
            # a path within that package, points to the file we depend on
            "/bin/hello",
        )

class Cowsay(DependencyBase):
    def ensure_path(nix: Nix, log: Logger) -> Path:
        nix.build("cowsay", "/bin/cowsay")

class GreeterClosure(ClosureBase):

    hello: Hello
    cowsay: Cowsay

    def __init__(self, nix: Nix, log: Logger):
        self.hello = Hello()
        self.cowsay = Cowsay()


        log.info(f"Preparing {super().name}'s closure'")
        items = []
        for name, item in ["hello", "cowsay"]:
            path_to_exe = nix.build(name, f"/bin/{name}")
            self.setattr(name, path_to_exe)
        super().__init__(*items)
        log.info("closure setup complete")


class HelloTool(Tool):
    """
    Create a tool class for each subprocess you will invoke via this cell's
    python interface.
    """

    def __init__(self, closure: HelloClosure, log: Logger):
        super().__init__(name="hello", path=closure.hello.path, log=log)


class HelloCell(CellBase):
    """ """

    hello: HelloTool

    def setup(self, closure: HelloClosure, log: Logger):
        self.hello_tool = Hello(closure, log)
