import math
import json
import operator


def get_distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d


class ResultFilters:

    @classmethod
    def filter_location(cls, requests, coordinates_pickup=None, coordinates_dropoff=None):
        request_list_score = []
        for request in requests:
            pickup_latlng = None
            try:
                pickup_latlng = json.loads(request.location_pickup)['latlng']
            except Exception:
                pass

            if pickup_latlng and coordinates_pickup:
                distance = get_distance(pickup_latlng, coordinates_pickup)

                request_list_score.append(
                    (distance, request)
                )
            elif coordinates_dropoff:
                min_distance = math.inf
                dropoffs = []
                try:
                    dropoffs = json.loads(request.location_dropoffs)
                except Exception:
                    pass
                for location_dropoff in dropoffs:
                    if not location_dropoff['latlng']:
                        continue
                    distance = get_distance(location_dropoff['latlng'], coordinates_dropoff)

                    min_distance = min(min_distance, distance)
                if not math.isinf(min_distance):
                    request_list_score.append(
                        (min_distance, request)
                    )

        # We take top 10
        return [request[1] for request in sorted(
            request_list_score, key=operator.itemgetter(0)
        )][:10]
