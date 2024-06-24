from typing import Protocol, runtime_checkable
from pytest import fixture
from pathlib import Path
from dataclasses import dataclass
from xdg_base_dirs import (
    xdg_cache_home,
    xdg_config_home,
    xdg_data_home,
    xdg_state_home,
)
from desmata.consts import desmata
from injector import Injector, Module, Binder, singleton

@runtime_checkable
class UserspaceFiles(Protocol):
    home: Path
    config: Path
    cache: Path
    data: Path
    state: Path

class UserspaceFilesBase:
    def __post_init__(self):
        for attr, attr_type in UserspaceFiles.__annotations__.items():
            if attr_type == Path:
                getattr(self, attr).mkdir(parents=True, exist_ok=True)

@dataclass
class DesmataFiles(UserspaceFilesBase):
    home: Path = Path.home()
    config: Path = xdg_config_home() / desmata
    cache: Path = xdg_cache_home() / desmata
    data: Path = xdg_data_home() / desmata
    state: Path = xdg_state_home() / desmata

    @staticmethod
    def sandbox(parent: Path | str) -> 'DesmataFiles':
        if isinstance(parent, str):
            parent = Path(parent)

        return DesmataFiles(
            home=parent,
            config=parent / "config" / desmata,
            cache=parent / "cache" / desmata,
            data=parent / "data" / desmata,
            state=parent / "state" / desmata,
        )

@fixture
def test_context(tmp_path) -> type[Module]:
    class TestContext(Module):
        def configure(self, binder: Binder) -> None:
            binder.bind(UserspaceFiles, to=DesmataFiles.sandbox(tmp_path), scope=singleton)
    return TestContext

@fixture
def run_context() -> type[Module]:
    class RunContext(Module):
        def configure(self, binder: Binder) -> None:
            binder.bind(UserspaceFiles, to=DesmataFiles(), scope=singleton)
    return RunContext

def test_local_files(test_context, run_context):
    test_injector = Injector([test_context])
    real_injector = Injector([run_context])
    test_files = test_injector.get(UserspaceFiles)
    real_files = real_injector.get(UserspaceFiles)
    print("test", test_files.config)
    print("real", real_files.config)

