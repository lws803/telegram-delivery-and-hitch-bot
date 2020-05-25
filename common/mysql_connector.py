import logging
import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from common.exceptions import SessionRollBackException

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class MySQLConnector:
    def __init__(self):
        self.session = None
        self._start_session()

    def _start_session(self):
        mysql_engine = create_engine(
            os.environ.get('MYSQL_PROD')
        )
        try:
            self.session = sessionmaker(bind=mysql_engine)
        except Exception:
            logger.warning(str(Exception))


    @contextmanager
    def session(self):
        if not self.session:
            self._start_session()
        session = self.session()
        try:
            yield session
            session.commit()
        except Exception:
            logger.warning(str(Exception))
            session.rollback()
            raise
        finally:
            session.close()
