from desmata.interface import Closure, Dependency
from desmata.protocols import (
    CellFactory,
    DBFactory,
    SpecificCell,
    UserspaceFiles,
    Loggers, )
from desmata.exceptions import BadCellClassException
from sqlalchemy import Engine
from pathlib import Path
import importlib


class DefaultCellFactory(CellFactory):
    userspace: UserspaceFiles
    db_factory: DBFactory
    _engine: Engine | None = None

    def __init__(self, log: Loggers, userspace: UserspaceFiles, db_factory: DBFactory):
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

    @staticmethod
    def _get_closure_type(CellType: type[SpecificCell]) -> type[Closure]:
        closure_types = []
        for base in CellType.__orig_bases__:
            for arg in base.__args__:
                if issubclass(arg, Closure):
                    closure_types.append(arg)

        if len(closure_types) != 1:
            raise BadCellClassException(
                f"Expected exactly one closure type for "
                f"cell type {CellType}, instead got {closure_types}. "
                "Cells should have Cell[SomeClosure] as a base class, "
                "where SomeClosure has Closure as a base class"
            )
        return closure_types[0]

    def _get_dependency(self, DependencyType: type[Dependency]):
        raise NotImplementedError()


    @staticmethod
    def _get_dependency_types(ClosureType: type[Closure]) -> dict[str, Dependency]:
        dependency_types: dict[str, Dependency] = {}
        print("got:", ClosureType)
        for attr, annotated_type in ClosureType.__annotations__.items():
            if issubclass(annotated_type, Dependency):
                dependency_types[attr] = annotated_type
        return dependency_types

    def get(self, CellType: type[SpecificCell]) -> SpecificCell:
        module_name = CellType.__module__
        module = importlib.import_module(module_name)
        name = self._cell_name(Path(module.__file__))

        ClosureType = DefaultCellFactory._get_closure_type(CellType)
        dependency_types = DefaultCellFactory._get_dependency_types(ClosureType)
        dependencies = {k: self._get_dependency(v) for k, v in dependency_types.items()} #closure = ClosureType(name=name, ...)
