import requests
from config import creds
import pandas as pd

url = 'https://ws.audioscrobbler.com/2.0/?method=user.get{}&user={}&api_key={}&limit={}&extended={}&page={}&format=json'
limit = 200 #api lets you retrieve up to 200 records per call
extended = 0 #api lets you retrieve extended data for each track, 0=no, 1=yes
page = 1 #page of results to start retrieving at

method = 'topartists'
request_url = url.format(method, creds['user'], creds['api_key'], limit, extended, page)
artist_names = []
play_counts = []
response = requests.get(request_url).json()
for item in response[method]['artist']:
    artist_names.append(item['name'])
    play_counts.append(item['playcount'])

top_artists = pd.DataFrame()
top_artists['artist'] = artist_names
top_artists['play_count'] = play_counts
top_artists.to_csv('data/lastfm_top_artists.csv', index=None, encoding='utf-8')