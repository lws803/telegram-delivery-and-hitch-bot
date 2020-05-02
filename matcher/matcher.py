import redis
from datetime import datetime
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class Matcher:
    def __init__(self):
        self.redis_connector = redis.Redis(host='localhost', port=6379, db=0)

    def add_match(self, my_chat_id, other_chat_id):
        epoch = datetime.utcfromtimestamp(0)
        def unix_time_millis(dt):
            return (dt - epoch).total_seconds() * 1000.0
        try:
            self.redis_connector.set(
                f'{my_chat_id}:{other_chat_id}', unix_time_millis(datetime.now())
            )
        except Exception as e:
            logger.warning(str(e))

    def check_match(self, my_chat_id, other_chat_id):
        try:
            match = self.redis_connector.get(f'{other_chat_id}:{my_chat_id}')
        except Exception as e:
            logger.warning(str(e))
        if match:
            return other_chat_id
        return None

    def delete_match(self, chat_id_1, chat_id_2):
        self.redis_connector.delete(f'{chat_id_1}:{chat_id_2}')
        self.redis_connector.delete(f'{chat_id_2}:{chat_id_1}')

    def delete_match_by_key(self, key):
        self.redis_connector.delete(str(key))

    def get_match_update_date(self, key):
        try:
            if self.redis_connector.get(str(key)):
                return float(self.redis_connector.get(str(key)))
        except Exception as e:
            logger.warning(str(e), str(key))

        return None

    def get_keys(self):
        return self.redis_connector.keys()
