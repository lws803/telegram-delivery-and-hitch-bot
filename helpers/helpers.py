import json
import logging

import geocoder

from common.constants import RoleType, StateType
from common.exceptions import InvalidCommandException, NoRequestExistException
from common.messages import Errors
from common.models import Request

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def get_location(text_location):
    # FIXME: Hack to refine and confine searches to singapore
    try:
        latlng = geocoder.google(text_location + ' singapore').latlng
        if not latlng:
            logger.warning(f'Cant find coordinates for {str(text_location)}')
        return dict(
            text=text_location,
            latlng=latlng
        )
    except Exception as e:
        logger.warning(str(e))

    return dict(
        text=text_location,
        latlng=None
    )


def get_location_json(text_location):
    return json.dumps(get_location(text_location))


def get_locations_json(text_locations):

    return json.dumps([
        get_location(text_location)
        for text_location in text_locations
    ])


def check_request_exists(db_session, update):
    curr_request = (
        db_session.query(Request)
        .filter_by(
            chat_id=update.message.chat_id,
            state=StateType.ACTIVE,
        )
        .one_or_none()
    )
    if not curr_request:
        logger.warning(f'No request found for {update.message.chat_id}')
        update.message.reply_text(Errors.NO_REQUEST_FOUND)
        raise NoRequestExistException


def check_search_user_valid(db_session, update):
    curr_request = (
        db_session.query(Request)
        .filter_by(
            chat_id=update.message.chat_id,
            state=StateType.ACTIVE,
        )
        .one_or_none()
    )
    if curr_request.role == RoleType.CUSTOMER:
        logger.warning(f'Customer used an invalid command {update.message.chat_id}')
        update.message.reply_text(Errors.FEATURE_INVALID % 'drivers')
        raise InvalidCommandException
