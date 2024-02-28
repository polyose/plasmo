import json
from dataclasses import dataclass, fields  # for things we don't need to serialize
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

@dataclass
class Home:
    """
    Desmata stores data in the local filesystem.
    A 'Home' object contains the various paths that it might use.

    Deleting these dirs is a way to clear any state that desmata may
    have stored on your system.

    To create a sandboxed desmata for testing, initialize desmata with
    A 'Home' object that is separate from any of the XDG recommended
    directories, see: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    """

    config: Path = xdg_config_home() / desmata
    cache: Path = xdg_cache_home() / desmata
    data: Path = xdg_data_home() / desmata
    state: Path = xdg_state_home() / desmata

    def __post_init__(self):
        self.mkdirs()
        (self.config / "config.json").write_text(
            json.dumps(Config().model_dump(), indent=2)
        )

    @staticmethod
    def sandbox(parent: Path | str) -> "Home":
        if isinstance(parent, str):
            parent = Path(parent)
        return Home(
            config=parent / "config" / desmata,
            cache=parent / "cache" / desmata,
            data=parent / "data" / desmata,
            state=parent / "state" / desmata,
        )

    def mkdirs(self):
        for field in fields(self):
            cast(Path, getattr(self, field.name)).mkdir(parents=True, exist_ok=True)

    def get_config(self):
        return Config.model_validate_json((self.config / "config.json").read_text())

    def root(self) -> str:
        """
        A user-facing string to communicate where desmata is rooted.
        Typically this will be their home dir but it might be different 
        if desmata is under test.
        """

        # from all paths above
        strings = [
            str(cast(Path, getattr(self, field.name)).resolve())
            for field in fields(self)
        ]

        # return the longest common substring (starting from the left)
        reference = strings[0]
        for i in range(len(reference)):
            substring = reference[:i+1]
            if all(s.startswith(substring) for s in strings):
                common_substring = substring
            else:
                return common_substring
        return reference

@dataclass
class AppContext:

    @staticmethod
    def from_typer(ctx: typer.Context) -> 'AppContext':
        return ctx.obj
        

    home: Home
    log: Logger
