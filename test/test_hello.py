from desmata.config import Home
from desmata import get_closure
from .samples.prokaryote.desmata import HelloCell, HelloClosure


def test_install(tmp_path):
    home = Home.sandbox(tmp_path)
    hello_closure = HelloClosure(home=home)
    hello_cell = HelloCell(hello_closure)
    assert hello_cell.hello() == "hello"
