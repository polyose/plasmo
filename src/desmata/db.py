from sqlmodel import (
    SQLModel,
    create_engine,
)
from sqlalchemy.engine import Engine

# SQLModel.metadata_create_all needs this:
from desmata import models  # noqa: F401
from desmata.protocols import DBFactory, Loggers, UserspaceFiles


class LocalSqlite(DBFactory):
    log: Loggers
    userspace: UserspaceFiles

    @property
    def file(self) -> str:
        return str(self.userspace.state / "cells.db").absolute()


    def __init__(self, log: Loggers, userspace: UserspaceFiles):
        self.log = log.specialize("dbfactory.sqlite")

    def delete_db(self) -> None:
        self.file.unlink()

    def get_engine(self) -> Engine:
        connection_string = f"sqlite://{self.file}"
        self.log.msg.debug(f"creating engine from string: {connection_string}")
        engine = create_engine(connection_string)
        self.log.msg.debug("initializing tables")

        # relies on the models having been imported already
        SQLModel.metadata.create_all(engine)

        return engine


        
