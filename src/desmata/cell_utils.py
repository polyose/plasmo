from desmata.protocols import CellContext
from desmata.nix import Nix

def get_nix(context: CellContext) -> Nix:
    return Nix(cwd=context.cell_dir, log=context.loggers.proc)
