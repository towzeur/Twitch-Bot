import requests
from cnst import CLIENT_ID, ClIENT_SECRET


class TwitchApiWrapper:
    BASE = 'https://api.twitch.tv/kraken'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def is_online(self, channel):
        url = self.BASE + '/streams/' + channel
        r = requests.get(url, params={'client_id': self.client_id})
        #print(r.url)
        if r.status_code == 200:
            # r.text          #Retourne le contenu en unicode
            # r.content       #Retourne le contenu en bytes
            # r.json          #Retourne le contenu sous forme json
            # r.headers       #Retourne le headers sous forme de dictionnaire
            # r.status_code   #Retourne le status code
            return bool(r.json()['stream'])


if __name__ == '__main__':
    wrp = TwitchApiWrapper(CLIENT_ID, ClIENT_SECRET)

    print(wrp.is_online('towzeur'))
    print(wrp.is_online('saltyteemo'))
