import logging
import json

import geocoder

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def get_location(text_location):
    # FIXME: Hack to refine and confine searches to singapore
    try:
        latlng = geocoder.google(text_location + ' singapore').latlng
        if not latlng:
            logger.warning(f'Cant find coordinates for {str(latlng)}')
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
