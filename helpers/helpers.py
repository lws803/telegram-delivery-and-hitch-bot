import logging
import json

import geocoder

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def get_location(text_location):
    text_location += ' singapore'
    # FIXME: Hack to refine and confine searches to singapore
    latlng = None
    try:
        latlng = geocoder.google(text_location).latlng
    except Exception as e:
        logger.warning(str(e))

    location_dict = dict(
        text=text_location,
        latlng=latlng
    )
    return location_dict


def get_location_json(text_location):
    return json.dumps(get_location(text_location))


def get_locations_json(text_locations):

    return json.dumps([
        get_location(text_location)
        for text_location in text_locations
    ])
