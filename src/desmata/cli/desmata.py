import typer
from desmata.cli.common import cli_logger

app = typer.Typer()

@app.command()
def ls(verbose: bool =  typer.Option(False, "--verbose", "-v")):
    log = cli_logger(verbose=verbose)
    log.info("desmata command: ls")

def main():
    app()
