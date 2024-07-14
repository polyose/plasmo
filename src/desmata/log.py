import logging
from desmata.protocols import Loggers
from rich.highlighter import NullHighlighter
from rich.logging import Console, RichHandler

class LoggersBase(Loggers):

    proc: logging.Logger
    msg: logging.Logger

    def specialize(self, name: str) -> Loggers:
        self.proc = self.proc.getChild(name)
        self.msg = self.msg.getChild(name)
        return self

class TestLoggers(LoggersBase, Loggers):
    def __init__(self):
        self.proc = logging.getLogger("test.proc")
        self.msg = logging.getLogger("test.msg")
        for logger in [self.proc, self.msg]:
            logger.propagate = False
            logger.addHandler(
                RichHandler(
                    show_time=False,
                    highlighter=NullHighlighter(),
                    console=Console(stderr=True),
                    show_path=True,
                    show_level=True,
                )
            )
            logger.setLevel(logging.DEBUG)
