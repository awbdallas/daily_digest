import requests

from json import loads

endpoint = 'https://hacker-news.firebaseio.com/v0/'

request_type = [ 'newstories', 'topstories', 'beststories', 'jobstories',
                'askstories', 'showstories']

def get_posts(passed_type='topstories', number_of=5):
    if passed_type in request_type:
        response = requests.get(endpoint + passed_type + '.json')
        if response.status_code != 200:
            raise requests.exceptions.HTTPError("Failed stories request")
        else:
            json_response = loads(response.text)
            items = json_response[:number_of]
            urls = [endpoint + 'item/' + str(item) + '.json' for item in items]
            try:
                payload = []
                for url in urls:
                    payload.append(loads(requests.get(url).text))
                return payload
            except:
                raise requests.exceptions.HTTPError("Error getting items")
    else:
        raise ValueError("Invalid Type of Request")
