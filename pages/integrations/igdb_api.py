import requests


class IgdbAPI:
    def __init__(self):
        self.__url = 'https://api.igdb.com/v4/games'
        self.__headers = {
            'Client-ID': 'n5eaou9kgy7ciieacwt5tm4yxuk6bp',
            'Authorization': 'Bearer 824dvniujkhmcnjl48qyvpop0qi0qc'
        }

    def get_games_test(self, data):
        games = requests.post(self.__url, headers=self.__headers, data=data)
        return games
