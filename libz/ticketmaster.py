import time
from config import TICKETMASTER_API_KEY
from common import call

TICKETMASTER_API_URL = 'http://app.ticketmaster.com/discovery/v2/'
EVENTS_FULL_URL = TICKETMASTER_API_URL + 'events.json?apikey=' + TICKETMASTER_API_KEY


class Ticketmaster:

    def get_events(self, keywords, country='fi'):
        event_data = []

        url = EVENTS_FULL_URL + '&locale=' + country

        for keyword in keywords:
            full_url = url + '&keyword=' + keyword

            response = call('get', full_url)
            response_json = response.json()
            if response_json['page']['totalElements'] == 0:
                continue
            time.sleep(1)
            for event in response_json['_embedded']['events']:
                venue_list = []

                event_dict = {
                    'name': event['name'],
                    'artist_name': keyword,
                    'url': event['url'],
                }

                if 'dates' in event.keys():
                    event_dict['datetime'] = event['dates']['start']['localDate'] or '' + " " + event['dates']['start']['localTime'] or ''

                if 'images' in event.keys():
                    event_dict['image_url'] = event['images'][0]['url'] or ''

                if '_embedded' in event.keys():
                    for venue in event['_embedded']['venues']:
                        venue_dict = {}
                        if 'name' in venue.keys():
                            venue_dict['name'] = venue['name'] or ''

                        if 'city' in venue.keys():
                            venue_dict['city'] = venue['city']['name'] or ''

                        if 'country' in venue.keys():
                            venue_dict['country'] = venue['country']['name'] or ''

                        if 'address' in venue.keys():
                            venue_dict['address'] = venue['address']['line1'] or ''

                        if 'location' in venue.keys():
                            venue_dict['longitude'] = venue['location']['longitude'] or ''
                            venue_dict['latitude'] = venue['location']['latitude'] or ''

                        if venue_dict:
                            venue_list.append(venue_dict)

                event_dict['venues'] = venue_list

                event_data.append(event_dict)

        return event_data
