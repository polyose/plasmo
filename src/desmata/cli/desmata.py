import typer
from desmata.cli.common import callback
from desmata.config import AppContext
from desmata.docs import view, generate
from enum import StrEnum, auto

app = typer.Typer(callback=callback)


@app.command()
def ls(ctx: typer.Context):
    app = AppContext.from_typer(ctx)
    app.log.info("desmata command: ls")


class DocsAction(StrEnum):
    view = auto()
    generate = auto()


@app.command()
def docs(ctx: typer.Context, action: DocsAction):
    app = AppContext.from_typer(ctx)
    match action:
        case DocsAction.view:
            view(app)
        case DocsAction.generate:
            generate(app)
        case otherwise:
            raise NotImplementedError(f"whats {otherwise}")


def cli():
    app()
