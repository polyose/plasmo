from logging import DEBUG, INFO, Formatter, Logger, StreamHandler, getLogger

import typer

from desmata.config import AppContext, Home


def cli_logger(verbose: bool) -> Logger:
    """
    Desmata is dependency-injected, a logger is one such dependency.
    Call this to get one.

    :return: A logger to be used when desmata is invoked via the CLI.
    """
    log = getLogger("  desmata.cli")
    if verbose:
        log.setLevel(DEBUG)
    else:
        log.setLevel(INFO)
    handler = StreamHandler()
    formatter = Formatter("%(name)s: %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


def callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    log = cli_logger(verbose=verbose)
    ctx.obj = AppContext(home=Home(), log=log)
