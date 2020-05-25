import logging
import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class MySQLConnector:
    def __init__(self):
        mysql_engine = create_engine(
            os.environ.get('MYSQL_PROD')
        )
        try:
            self.Session = sessionmaker(bind=mysql_engine)
        except Exception:
            logger.warning(str(Exception))

    @contextmanager
    def session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            logger.warning(str(Exception))
            session.rollback()
            raise
        finally:
            session.close()
