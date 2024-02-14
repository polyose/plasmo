import typer
import logging
from logging import Formatter, StreamHandler, getLogger, Logger



app = typer.Typer()


def _cli_logger(verbose: bool) -> Logger:
    """
    Desmata is dependency-injected, a logger is one such dependency.
    Call this to get one.
        
    :return: A logger to be used when desmata is invoked via the CLI.
    """
    log = getLogger("  desmata.cli")
    if verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    handler = StreamHandler()
    formatter = Formatter("%(name)s: %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


@app.command()
def init(verbose: bool =  typer.Option(False, "--verbose", "-v")):
    log = _cli_logger(verbose=verbose)
    log.debug("cli: init")

def cli():
    app()
