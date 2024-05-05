from abc import ABC, abstractmethod
from pathlib import Path
from desmata.nix import Nix

from pydantic import BaseModel


class Dependency(BaseModel, ABC):

    id: str
    hash: str | None
    path: Path

    @staticmethod
    @abstractmethod
    def ensure_path(nix: Nix) -> Path:
        raise NotImplementedError()

    @staticmethod
    def get_id(path: Path) -> str:
        if "/nix/store" not in path.name:
            raise NotImplementedError(
                f"Unable to determine a suitable dependency ID from {path.resolve()}, "
                "please override get_id(Path) on the corresponding subclass of Dependency"
            )
        else:
            return path.name.replace("/nix/store/", "")


class Closure(BaseModel, ABC):

    local_name: str
    dependencies: list[Dependency]
    hash: str
    nucleus_hash: str

    @property
    def dependency_inputs(self) -> list[str]:
        return ["./flake.nix", "./flake.lock"]

    @property
    def nucleus(self) -> list[str]:
        return ["./flake.nix", "./flake.lock"]

    @property
    def membrane(self) -> list[str]:
        return ["./cell.py"]

def is_same_file(a: Path, b: Path) -> bool:
    """"
    :return: True if the given paths represent the same file
    """
    a_stat = a.stat()
    b_stat = b.stat()
    return (a_stat.st_ino == b_stat.st_ino) and (a_stat.st_dev == b_stat.st_dev)



class Cell(ABC):
    closure: Closure

Cell.__doc__ = """
"""
