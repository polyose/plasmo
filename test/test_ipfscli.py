from pathlib import Path

from desmata.builtins.cell import DesmataBuiltins
from desmata.get import c
from pytest import fixture


@fixture
def builtins() -> DesmataBuiltins:
    return from_cell_class(DesmataBuiltins)
    
def test_ipfs_hash(tmp_path: Path, builtins: DesmataBuiltins):
    f = tmp_path / "foo"
    f.write_text("bar")
    builtins.ipfs.hash(f)





