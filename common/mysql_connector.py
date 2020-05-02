import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class MySQLConnector:
    def __init__(self):
        mysql_engine = create_engine(
            os.environ.get('MYSQL_PROD')
        )
        self.Session = sessionmaker(bind=mysql_engine)

    @contextmanager
    def session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
