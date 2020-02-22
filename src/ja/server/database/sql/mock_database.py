import testing.postgresql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from ja.server.database.sql.database import SQLDatabase

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)


class MockDatabase(SQLDatabase):

    def __init__(self) -> None:
        super().__init__()
        self.postgresql = Postgresql()
        # connect to PostgreSQL
        self.engine = create_engine(self.postgresql.url())
        self.scoped = scoped_session(sessionmaker(self.engine))
        SQLDatabase._metadata.create_all(self.engine)
        self.session = self.scoped()
