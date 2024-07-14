from desmata.protocols import CellFactory, DBFactory, SpecificCell, UserspaceFiles, Loggers
from sqlalchemy import Engine
from pathlib import Path
import importlib

class DefaultCellFactory(CellFactory):

    userspace: UserspaceFiles
    db_factory: DBFactory
    _engine: Engine | None = None

    def __init__(self, log: Loggers, userspace: UserspaceFiles, db_factory: DBFactory ):
        self.log = log
        self.userspace = userspace
        self.db_factory = db_factory

    @property
    def engine(self) -> Engine:
        if not self._engine:
            self._engine = self.db_factory.get_engine()
        return self._engine

    def _cell_name(self, cell_class_file: Path):

        parts = cell_class_file.parent.parts  # /foo/bar/baz/cell.py
        name_candidates = [
            "/".join(parts[-1 * i :]) for i in range(1, len(parts))
        ]  # ["baz", "bar/baz", "foo/bar/baz"]
        self.log.msg.debug(f"Cell name candidates: {name_candidates}")

    def get(self, CellType: type[SpecificCell]) -> SpecificCell:
        module_name = CellType.__module__
        module = importlib.import_module(module_name)
        self._cell_name(Path(module.__file__))

