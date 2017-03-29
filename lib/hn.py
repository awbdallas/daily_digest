import requests

from json import loads
from tabulate import tabulate
from lib.source_interface import Source_Interface


class HN(Source_Interface):
    """HN REST API documenation can be found here: https://github.com/HackerNews/API"""


    def __init__(self):
        """
        Few notes: I've been setting up trying to make everything in this class
        private outside of get_digest for a reason. Not sure if it's the best design
        idea, but I've extended that to object variables as well...awkward?
        """
        self._endpoint = 'https://hacker-news.firebaseio.com/v0/'
        self._hn_link = 'https://news.ycombinator.com/item?id='
        self._required_item_fields = [
            'id', 'title', 'url'
        ]

    def get_digest(self):
        """
        Purpose: get the best stories for hacker news
        Parameters: number of stories is an optional argument
        Returns: list of items
        Special Notes: best_stories just return a json array of numbers
        """
        table_headers = ['Title', 'Url', 'Link to Post']
        table_data = []

        items = self._get_best_stories()
        try:
            for item in items:
                table_data.append([
                    item['title'],
                    item['url'],
                    self._hn_link + str(item['id'])
                ])
            return tabulate(table_data, table_headers, tablefmt='html')
        except (RequestStoriesError, RequestItemError):
            return 'Failed Requests for HN'
        except (ResponseStoriesError, ResponseItemError):
            return 'Failed Responses for HN'
        except:
            return 'Failed to get HN'

    def _get_best_stories(self, number_of_stories=5):
        """
        Purpose: get the best stories for hacker news
        Parameters: number of stories is an optional argument
        Returns: list of items
        Special Notes: best_stories just return a json array of numbers
        """
        response = requests.get(self._endpoint + 'beststories.json')

        if response.status_code != 200:
            raise RequestStoriesError('Failed Request for Stories')
        json_response = loads(response.text)
        if not isinstance(json_response, list) and len(json_response) > 0:
            raise ResponseStoriesError('Failed Response to Stories')

        items = []
        for item in json_response:
            item = self._get_items(item)
            if item:
                items.append(item)
            if len(items) == number_of_stories:
                return items
        return items

    def _get_items(self, item, required_fields=None):
        """
        Purpose: Get items from requests
        Parameters: item number
        Returns: the item in dict format after checking for required_fields
        """
        if not required_fields:
            required_fields = self._required_item_fields

        url = self._endpoint + 'item/' + str(item) + '.json'
        response = requests.get(url)

        if response.status_code != 200:
            raise RequestItemError('Failed Request to Items')

        item_dict = loads(response.text)
        if len(item_dict) == 0 and isinstance(item_dict, dict):
            raise RequestItemError('Failed response to Items')

        for field in required_fields:
            if not item_dict.get(field, None):
                return None

        return item_dict


class RequestStoriesError(Exception):
    pass

class ResponseStoriesError(Exception):
    pass

class RequestItemError(Exception):
    pass

class ResponseItemError(Exception):
    pass
