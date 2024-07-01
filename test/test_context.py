
from pathlib import Path

from injector import Binder, Injector, Module, singleton
from pytest import fixture

from desmata.builtins.cell import DesmataBuiltins
from desmata.db import LocalSqlite
from desmata.fs import DesmataFiles
from desmata.log import TestLoggers
from desmata.protocols import DBFactory, Loggers, UserspaceFiles


@fixture
def components(tmp_path: Path) -> Injector:
    class TestContext(Module):
        def configure(self, binder: Binder) -> None:
            binder.bind(Loggers, to=TestLoggers, scope=singleton)
            binder.bind(DBFactory, to=LocalSqlite, scope=singleton)
            binder.bind(
                UserspaceFiles, to=DesmataFiles.sandbox(tmp_path), scope=singleton
            )

    return Injector[TestContext]


def test_local_files(components: Injector):
    files = components.get(UserspaceFiles)
    loggers = components.get(Loggers)
    cell_files = files.home_for(cell_type=DesmataBuiltins)
    loggers.msg.info(cell_files)
