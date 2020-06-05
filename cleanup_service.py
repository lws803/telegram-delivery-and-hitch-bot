import logging
import time
from datetime import datetime

from common.constants import StateType
from common.models import Blacklist, Report, Request
from common.mysql_connector import MySQLConnector
from matcher.matcher import Matcher

INTERVAL_MINUTE = 10

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    match_session = Matcher()
    epoch = datetime.utcfromtimestamp(0)

    def unix_time_millis(dt):
        return (dt - epoch).total_seconds() * 1000.0

    while True:
        # Check staleness in redis
        for key in match_session.get_keys():
            key = key.decode('utf-8')
            if ':' in key and match_session.get_match_update_date(key) is not None:
                time_diff = abs(
                    match_session.get_match_update_date(key) - unix_time_millis(datetime.utcnow())
                )
                # Matched for more than an hour
                if time_diff > (60 * 60 * 1000):
                    try:
                        logger.info(f'Delete {key} from redis...')
                        match_session.delete_match_by_key(key)
                    except Exception as e:
                        logger.warning(str(e))

        # Check staleness
        mysql_connector = MySQLConnector()
        with mysql_connector.session() as db_session:
            stale_chat_ids = []
            for request in db_session.query(Request).all():
                if request.state == StateType.DONE:
                    continue
                if request.time is not None:
                    time_diff = (datetime.utcnow() - request.time).total_seconds()
                    if time_diff > (60 * 60):
                        stale_chat_ids.append(request.chat_id)
                else:
                    time_diff = (datetime.utcnow() - request.last_updated).total_seconds()
                    # 1 Hour allowed for merchants
                    if time_diff > (60 * 60):
                        stale_chat_ids.append(request.chat_id)

            for chat_id in stale_chat_ids:
                logger.info(f'Setting {chat_id} to STALE')
                request = db_session.query(Request).filter_by(chat_id=chat_id).first()
                request.state = StateType.DONE

            # Check blacklist
            for chat in db_session.query(Report).all():
                chat_id = chat.chat_id
                if chat.report_count > 10:
                    existing_ban = db_session.query(Blacklist).filter_by(
                        chat_id=chat_id
                    ).one_or_none()

                    if not existing_ban:
                        db_session.add(Blacklist(
                            chat_id=chat_id
                        ))
                        logger.info(f'Banning {chat_id}')
                    banned_request = db_session.query(Request).filter_by(chat_id=chat_id).first()
                    banned_request.state = StateType.DONE

            db_session.commit()
        time.sleep(INTERVAL_MINUTE * 60)
