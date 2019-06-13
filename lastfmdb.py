import sqlite3
import requests
from config import creds
import time
import unidecode

con = sqlite3.connect('/home/levo/Documents/projects/lastfm/data/lastfmscrobbles.db')
cur = con.cursor()
try:
    cur.execute('SELECT MAX(timestamp) FROM listens')
    from_date = cur.fetchone()[0] + 1
except sqlite3.OperationalError:
    from_date = 0
except TypeError:
    from_date = 0
    
def create_table():
    q = '''

        CREATE TABLE if not exists artists (
            id integer PRIMARY KEY AUTOINCREMENT,
            mbid TEXT DEFAULT NULL,
            name TEXT
        );

        CREATE TABLE if not exists tracks (
            id integer PRIMARY KEY AUTOINCREMENT,
            mbid TEXT,
            name TEXT,
            artist_id integer,
            album_id integer
        );

        CREATE TABLE if not exists albums (
            id integer PRIMARY KEY AUTOINCREMENT,
            mbid TEXT,
            name TEXT,
            artist_id integer
        );

        CREATE TABLE if not exists listens (
            id integer PRIMARY KEY AUTOINCREMENT,
            track_id integer,
            timestamp integer
        );
        '''
    cur.executescript(q)
    con.commit()
    return None

def get_lastfm_scrobbles():
    responses = []
    page = 1
    api_url = 'https://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user={}&api_key={}&limit=200&extended=0&page={}&format=json&from={}'.format(creds["user"],creds["api_key"], page, from_date)
    r = requests.get(api_url).json()
    total_pages = int(r['recenttracks']['@attr']['totalPages'])
    for page in range(1, total_pages + 1):
        print('Getting page {}'.format(page))
        api_url = 'https://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user={}&api_key={}&limit=200&extended=0&page={}&format=json&from={}'.format(creds["user"],creds["api_key"], page, from_date)
        r = requests.get(api_url)
        while 'error' in r.json().keys():
            print('Error: {}'.format(r.json()["message"]))
            time.sleep(r.elapsed.total_seconds())
            r = requests.get(api_url)
        responses.append(r)
        # print('Sleeping for {} seconds'.format(r.elapsed.total_seconds()))    
        time.sleep(0.5)
    return responses

def add_artist(artist):
    artist['#text'] = unidecode.unidecode(artist['#text'])
    q = 'SELECT id FROM artists WHERE name = ?'
    cur.execute(q, (artist['#text'],))
    artist_id = cur.fetchone()
    if artist_id is None:
        cur.execute('INSERT INTO artists (mbid, name) VALUES (? , ?)', (artist['mbid'], artist['#text']))
        cur.execute(q, (artist['#text'],))
        artist_id = cur.fetchone()
    return artist_id[0]

def add_album(album, artist_id):
    q = 'SELECT id FROM albums WHERE artist_id = ? AND name = ?'
    cur.execute(q,(artist_id, album['#text']))
    album_id = cur.fetchone()
    if album_id is None:
        cur.execute('INSERT INTO albums (mbid, name, artist_id) VALUES (?, ?, ?)', (album['mbid'], album['#text'], artist_id))
        cur.execute(q, (artist_id, album['#text']))
        album_id = cur.fetchone()
    return album_id[0]

def add_track(track, artist_id, album_id):
    q = 'SELECT id FROM tracks WHERE artist_id = ? AND name = ?'
    cur.execute(q ,(artist_id, track['name']))
    track_id = cur.fetchone()
    if track_id is None:
        cur.execute('INSERT INTO tracks (mbid, name, artist_id, album_id) VALUES (?, ?, ?, ?)', (track['mbid'], track['name'], artist_id, album_id))
        cur.execute(q ,(artist_id, track['name']))
        track_id = cur.fetchone()
    return track_id[0]

def add_listen(track, track_id):
    cur.execute('INSERT OR IGNORE INTO listens (timestamp, track_id) VALUES (?, ?)', (track['date']['uts'], track_id))

def main():
    create_table()
    scrobbles = get_lastfm_scrobbles()
    for response in scrobbles:
        tracks = response.json()
        for track in tracks['recenttracks']['track']:
            if 'date' in track.keys():
                artist_id = add_artist(track['artist'])
                album_id = add_album(track['album'], artist_id)
                track_id = add_track(track, artist_id, album_id)
                add_listen(track, track_id)
    con.commit()
    
if __name__ == "__main__":            
    main()
    con.close()