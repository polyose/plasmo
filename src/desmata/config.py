import json
from dataclasses import dataclass, fields, Field  # for things we don't need to serialize
from logging import Logger
from pathlib import Path
from typing import cast

import typer
from pydantic import BaseModel  # for things we do need to serialize
from xdg_base_dirs import (
    xdg_cache_home,
    xdg_config_home,
    xdg_data_home,
    xdg_state_home,
)

from desmata.consts import desmata


class Config(BaseModel):
    placeholder: str = "placeholder"


@dataclass(kw_only=True)
class Home:
    dir: Path = Path.home()
    config: Path = xdg_config_home() / desmata
    cache: Path = xdg_cache_home() / desmata
    data: Path = xdg_data_home() / desmata
    state: Path = xdg_state_home() / desmata

    def __post_init__(self):
        self._mkdirs()

    def _mkdirs(self):
        for field in fields(self):
            cast(Path, getattr(self, field.name)).mkdir(parents=True, exist_ok=True)


@dataclass(kw_only=True)
class DesmataHome(Home):
    """
    Desmata stores data in the local filesystem.
    A 'Home' object contains the various paths that it might use.

    Deleting these dirs is a way to clear any state that desmata may
    have stored on your system.

    To create a sandboxed desmata for testing, initialize desmata with
    A 'Home' object that is separate from any of the XDG recommended
    directories, see: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    """

    desmata_config: Config

    def __post_init__(self):
        desmata_config = self.config / "config.json"
        if not desmata_config.exists():
            desmata_config.write_text(json.dumps(Config().model_dump(), indent=2))
        self.desmata_config = Config.model_validate_json(desmata_config.read_text())

    @staticmethod
    def sandbox(parent: Path | str, subfolder: str | None = desmata) -> "Home":
        if isinstance(parent, str):
            parent = Path(parent)

        return Home(
            dir=parent,
            config=parent / "config" / desmata,
            cache=parent / "cache" / desmata,
            data=parent / "data" / desmata,
            state=parent / "state" / desmata,
        )


class CellHome(Home):
    cell_name: str

    def __init__(self, cell_name: str):
        """
        Each cell gets its own home directory, this prevents configs from one
        cell (or elsewhere in the system) from affecting behavior in another
        cell.
        """
        cell_home_dir = DesmataHome().data / "cell_homes" / cell_name
        boundary = len(Path.home().parts)

        def rehome(xdg: Path):
            return Path.joinpath(cell_home_dir, *xdg.parts[boundary:])

        self.cell_name = cell_name
        self.dir = cell_home_dir
        self.config = rehome(xdg_config_home())
        self.cache = rehome(xdg_cache_home())
        self.data = rehome(xdg_data_home())
        self.state = rehome(xdg_state_home())

    # TODO: think about whether we should warn about or dissalow tools that
    # update their home dir the initial idea was that config would happen once
    # on install and never again (to guard against function impurity) but maybe
    # it would be ok if some stat were cached on the local system?

    def env(self, path: Path | list[Path] = []) -> dict[str, str]:
        """
        Cell tools might not inherit env vars from the surrounding environment,
        instead they get this env.  This helps ensure that cells encapsulate
        their dependencies properly rather than depending on data from suprising
        places.
        """
        def to_str(path: Path) -> str:
            return str(path.resolve())

        pathvar =  ":".join(map(to_str, path)) if isinstance(path, list) else to_str(path)
        return {"HOME": to_str(self.dir), "PATH": pathvar}


@dataclass
class AppContext:
    @staticmethod
    def from_typer(ctx: typer.Context) -> "AppContext":
        return ctx.obj

    home: Home
    log: Logger
