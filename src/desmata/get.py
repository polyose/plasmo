from pathlib import Path
from typing import TypeAlias, TypeVar
from desmata.interface import Cell


SpecificCell = TypeVar("SpecificCell", bound=Cell)


def from_cell_class(CellType: type[SpecificCell]) -> SpecificCell:
    for attr in vars(CellType):
        print(attr)
    
