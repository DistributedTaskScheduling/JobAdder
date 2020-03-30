import testing.postgresql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from ja.server.database.sql.database import SQLDatabase
import logging
from typing import Dict

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)

logger = logging.getLogger(__name__)


class MockDatabase(SQLDatabase):

    def __init__(self, max_special_resources: Dict[str, int] = None) -> None:
        super().__init__(max_special_resources=max_special_resources)
        self.postgresql = Postgresql()
        # connect to PostgreSQL
        self.engine = create_engine(self.postgresql.url())
        self.scoped = scoped_session(sessionmaker(self.engine))
        SQLDatabase._metadata.create_all(self.engine)
        self.session = self.scoped()
        logger.info("connection to mock database")
