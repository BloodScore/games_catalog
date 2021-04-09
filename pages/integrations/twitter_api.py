import requests
from django.conf import settings


class TwitterApi:
    def __init__(self):
        self.__url = 'https://api.twitter.com/2/tweets/search/recent'
        self.__headers = {
            'Authorization': f'{settings.TWITTER_BEARER_TOKEN}'
        }

    def get_tweets(self, game_name):
        payload = {
            'query': f'#{game_name} lang:en',
            'tweet.fields': 'created_at',
            'expansions': 'author_id'
        }
        tweets = requests.get(self.__url, params=payload, headers=self.__headers).json()
        return tweets
