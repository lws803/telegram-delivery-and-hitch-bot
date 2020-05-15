import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from helpers.helpers import retry_on_connection_error


class MySQLConnector:
    def __init__(self):
        mysql_engine = create_engine(
            os.environ.get('MYSQL_PROD')
        )
        self.Session = sessionmaker(bind=mysql_engine)

    @contextmanager
    @retry_on_connection_error(3)
    def session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except OperationalError:
            raise
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
