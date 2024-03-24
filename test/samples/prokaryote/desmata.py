from logging import Logger

from desmata.interface import CellBase, ClosureBase, ClosureItem
from desmata.nix import Nix
from desmata.tool import Tool
from logging import Logger


class HelloClosure(ClosureBase):
    """
    If your cell needs anything besides desmata to be useful, define a closure
    to include it.
    """

    hello: ClosureItem

    def desmata_py():
        return __file__

    def __init__(self, nix:Nix, log: Log):
        log.info(f"Preparing {super().name}'s closure'")
        self.hello = ClosureDir.from_nix_build(nix.build("hello", "/bin/hello"))
        super().__init__(self.hello, **kwargs)
        log.info("closure setup complete")


class HelloTool(Tool):
    """
    Create a tool class for each subprocess you will invoke via this cell's
    python interface.
    """

    def __init__(self, closure: HelloClosure, log: Logger):
        super().__init__(name="hello", path=closure.hello.path, log=log)


class HelloCell(CellBase):
    """
        
    """
    hello: HelloTool

    def setup(self, closure: HelloClosure, log: Logger):
        self.hello_tool = Hello(closure, log)

