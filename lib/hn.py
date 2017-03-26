import requests

from json import loads

# API endpoint for hn.
# can grab link to documentation here: https://github.com/HackerNews/API
endpoint = 'https://hacker-news.firebaseio.com/v0/'

# Only really supporting stories
request_type = [ 'newstories', 'topstories', 'beststories', 'jobstories',
                'askstories', 'showstories']

required_item_fields = [
    'id', 'title', 'url'
]

def get_posts(passed_type='topstories', number_of=5):
    """
    Purpose:
    Parameters: What I'm trying to get storie wise. This is checked against
    request_type type. Also added is number of stories to get.
    Returns a list of dicts of things like ids and such that are returned
    Refer to api documentation for rough idea of what it will have
    """
    if not number_of in range(1, 500):
        raise ValueError("Number should be in range of 1 to 100")

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
                    holding_response  = requests.get(url)
                    if holding_response.status_code != 200:
                        raise requests.exceptions.HTTPError\
                                ("Failed item request")
                    holding_text = loads(holding_response.text)
                    to_append = True
                    for required_field in required_item_fields:
                        if required_field not in holding_text.keys():
                            to_append = False
                            break
                    if to_append:
                        payload.append(holding_text)
                return payload
            except:
                raise requests.exceptions.HTTPError("Error getting items")
    else:
        raise ValueError("Invalid Type of Request")
