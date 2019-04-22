import requests
from config import creds
import time
import json
import pandas as pd

page = 1
api_url = f'https://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user={creds["user"]}&api_key={creds["api_key"]}&limit=200&extended=0&page={page}&format=json'

r = requests.get(api_url).json()
total_pages = int(r['recenttracks']['@attr']['totalPages'])
print(f'{total_pages} to retrive')
responses = []
artist_names = []
album_names = []
track_names = []
timestamps = []

for page in range(1,total_pages + 1):
    print(f'Getting page {page}')
    api_url = f'https://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user={creds["user"]}&api_key={creds["api_key"]}&limit=200&extended=0&page={page}&format=json'
    print(api_url)
    r = requests.get(api_url)
    while 'error' in r.json().keys():
        print(f'Error: {r.json()["message"]}')
        time.sleep(r.elapsed.total_seconds())
        r = requests.get(api_url)
    responses.append(r)
    print(f'Sleeping for {r.elapsed.total_seconds()} seconds')    
    time.sleep(r.elapsed.total_seconds())

print(len(responses))
for response in responses:
    scrobbles = response.json()
    for scrobble in scrobbles['recenttracks']['track']:
        if 'date' in scrobble.keys():
            artist_names.append(scrobble['artist']['#text'])
            album_names.append(scrobble['album']['#text'])
            track_names.append(scrobble['name'])
            timestamps.append(scrobble['date']['uts'])


df = pd.DataFrame()
df['artist'] = artist_names
df['album'] = album_names
df['track'] = track_names
df['timestamp'] = timestamps
df['datetime'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')

df.to_csv('data/scrobbles.csv')