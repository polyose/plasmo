from logging import Formatter, StreamHandler, getLogger, Logger, DEBUG, INFO


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
