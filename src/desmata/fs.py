from dataclasses import dataclass
from pathlib import Path

from xdg_base_dirs import xdg_cache_home, xdg_config_home, xdg_data_home, xdg_state_home

from desmata.consts import desmata
from desmata.protocols import Loggers, UserspaceFiles


class CreatePathAttrs:
    def __post_init__(self):
        for attr, attr_type in UserspaceFiles.__annotations__.items():
            if attr_type == Path:
                path = getattr(self, attr)
                if not path.exists():
                    self.log.msg.debug(f"Creating {path}")
                    path.mkdir(parents=True)


@dataclass
class CellFiles(CreatePathAttrs):
    home: Path

    def env(self, path: Path | list[Path] = []) -> dict[str, str]:
        def to_str(path: Path) -> str:
            return str(path.resolve())

        pathvar = (
            ":".join(map(to_str, path)) if isinstance(path, list) else to_str(path)
        )
        return {"HOME": to_str(self.dir), "PATH": pathvar}


@dataclass
class DesmataFiles(CreatePathAttrs, UserspaceFiles):
    log: Loggers
    home: Path = Path.home()
    config: Path = xdg_config_home() / desmata
    cache: Path = xdg_cache_home() / desmata
    data: Path = xdg_data_home() / desmata
    state: Path = xdg_state_home() / desmata

    @staticmethod
    def sandbox(
        parent: Path | str, log: Loggers
    ) -> "DesmataFiles":
        """
        Instead of the user's home dir, use a parent path.
        Useful for testing.
        """
        if isinstance(parent, str):
            parent = Path(parent)

        return DesmataFiles(
            log=log,
            home=parent,
            config=parent / "config" / desmata,
            cache=parent / "cache" / desmata,
            data=parent / "data" / desmata,
            state=parent / "state" / desmata,
        )

    def __post_init__(self):
        super().__post_init__()

    # def home_for(self, *, cell_type: type[CellBase]) -> Path:
    #     # cell names might resemble the path of cell.py
    #     parts = cell_type.cell_path().parts  # /foo/bar/baz/cell.py
    #     name_candidates = [
    #         "/".join(parts[-1 * i :]) for i in range(1, len(parts))
    #     ]  # ["baz", "bar/baz", "foo/bar/baz"]
    #     self.log.msg.debug(f"Cell name candidates: {name_candidates}")

    #     # explore existing cells
    #     with Session(self.engine) as session:
    #         cells = session.exec(
    #             select(Cell).where(Cell.name.in_(name_candidates))
    #         ).all()
    #         self.log.msg.debug(f"found: {[x.name for x in cells]}")
