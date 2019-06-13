import pandas as pd
import sqlite3
import pytz
import spotipy
import spotipy.util as util
from funcy.seqs import first
from collections import namedtuple
from config import spotify_username as username, client_secret, client_id

song = namedtuple('song', ['artist', 'title'])
today = pd.to_datetime('today')
con = sqlite3.connect('/home/levo/Documents/projects/lastfm/data/lastfmscrobbles.db')
q = '''

SELECT 
	tracks.id AS 'Track ID',
	listens.timestamp AS 'Date Played',
	tracks.name AS Track,
	artists.name AS Artist
FROM listens
JOIN tracks ON listens.track_id = tracks.id
JOIN artists ON tracks.artist_id = artists.id
'''

scrobbles = pd.read_sql_query(q, con)
# Prepare data
scrobbles['Date Played'] = pd.to_datetime(scrobbles['Date Played'].astype(int), unit='s')
# Convert UTC timestamps to GMT
gmt = pytz.timezone('Europe/London')
scrobbles['Date Played'] = scrobbles['Date Played'].dt.tz_localize(pytz.utc).dt.tz_convert(gmt)
scrobbles['Date Played'] = scrobbles['Date Played'].dt.tz_localize(None)
scrobbles.sort_values(by='Date Played', ascending=False, inplace=True)
scrobbles.rename(columns={'Date Played': 'Last Played'}, inplace=True)

def play_counts(df):
    df['Play Count'] = df.groupby(['Track', 'Artist'], as_index=False)['Track ID'].transform('count')
    df.drop_duplicates('Track ID', inplace=True)
    return df


def last_played(df, days, not_within=False):
	delta = today - pd.Timedelta(days, unit='d')
	if not not_within:
		df = df[df['Last Played'] > delta]
	else:
		df = df[df['Last Played'] < delta]
	return df

def select_based_plays(df, plays, more_than=True):
	if more_than:	
		return df[df['Play Count'] > plays]
	else:
		return df[df['Play Count'] < plays]

def check_playlist_exists(playlist_name, playlists):
    playlist_names = [p['name'] for p in playlists]
    if playlist_name in playlist_names:
        return True
    else:
        return False


def generate_spotify_playlist(tracks, playlist_name):
    token = util.prompt_for_user_token(username,'playlist-modify-public' ,client_id=client_id,
    client_secret=client_secret,
    redirect_uri='http://localhost/')

    spotify = spotipy.Spotify(auth=token)

    format_search = [f'artist:{t.artist} track:{t.title}' for t in tracks]
    search_res = [spotify.search(q=t, type='track', limit=1) for t in format_search]
    track_ids = [(first(r.get('tracks', {}).get('items', {})) or {}).get('uri') for r in search_res if
                    r.get('tracks', {}).get('items')]

    chunks = [track_ids[x:x+100] for x in range(0, len(track_ids), 100)]
    user_playlists = spotify.user_playlists(username)
   
    if check_playlist_exists(playlist_name, user_playlists['items']):
        for p in user_playlists['items']:
            if p.get('name') == playlist_name:
                playlist_id = p.get('id')
    else:
        playlist = spotify.user_playlist_create(username, playlist_name)
        playlist_id = playlist.get('id')

    for chunk in chunks:
        # spotify.user_playlist_remove_all_occurrences_of_tracks(username, playlist_id, chunk)
        spotify.user_playlist_replace_tracks(username, playlist_id, chunk)

def df_to_list(playlist_df):
	playlist_df = playlist_df[['Artist', 'Track']]
	listed_values = playlist_df.values.tolist()
	track_tuples = [song(track[0], track[1]) for track in listed_values]
	return track_tuples

playlist = play_counts(scrobbles)
playlist = last_played(scrobbles, 14, True)
playlist = select_based_plays(playlist, 10)
playlist = playlist.sample(100)

tracks = df_to_list(playlist)
generate_spotify_playlist(tracks, 'alltimepopular')

recent_popular = last_played(scrobbles, 90)
recent_popular = play_counts(recent_popular)
recent_popular = select_based_plays(recent_popular, 5, True)
if len(recent_popular) > 99:
    recent_popular = recent_popular.sample(100)
elif len(recent_popular) > 0:
    tracks = df_to_list(recent_popular)
    generate_spotify_playlist(tracks, 'currentpopular')
