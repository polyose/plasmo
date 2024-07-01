from sqlmodel import (
    Engine,
    SQLModel,
    create_engine,
)

# SQLModel.metadata_create_all needs this:
from desmata import models  # noqa: F401
from desmata.protocols import DBFactory, Loggers, UserspaceFiles


class LocalSqlite(DBFactory):
    log: Loggers

    def __init__(self, log: Loggers):
        self.log = log.specialize("dbfactory.sqlite")

    def get_engine(self, userspace: UserspaceFiles) -> Engine:

        connection_string = f"sqlite://{(userspace.state / "cells.db").absolute()}"
        self.log.msg.debug(f"creating engine from string: {connection_string}")
        engine = create_engine(connection_string)
        self.log.msg.debug("initializing tables")

        # relies on the models having been imported already
        SQLModel.metadata.create_all(engine)

        return engine


        
