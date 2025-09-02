import pandas as pd
import pytz
import datetime
import matplotlib.pyplot as plt
import random

plt.style.use('ggplot')
SCROBBLES = '/home/levo/Documents/projects/lastfm/data/scrobbles.csv'
IMG_DIR = '/home/levo/Documents/projects/lastfm/images/slides'

def prepare_data():
    data = pd.read_csv(SCROBBLES)
    data = data.drop('timestamp', axis=1)
    data['timestamp'] = pd.to_datetime(data['datetime']) 
    data = data.drop('datetime', axis=1)
    data = data.replace(to_replace='Maxïmo Park', value='Maximo Park')
    data = data[data['artist'] != 'BBC Radio 4']
    data = data[data['artist'] != 'guardian.co.uk']
    data = data[data['artist'] != 'cnet.com']
    gmt = pytz.timezone('Europe/London')
    data['timestamp'] = data['timestamp'].dt.tz_localize(pytz.utc).dt.tz_convert(gmt)
    return data


def total_scrobbles_over_time(df, to_interval):
    artists_df = df.drop(['album', 'track', 'Unnamed: 0'], axis=1)
    artists_df = artists_df[artists_df['timestamp'] < f'{to_interval}']
    artist_counts = artists_df['artist'].value_counts()
    return artist_counts.head(20)


def create_bar_chart(df, count, end_date, ylimit):
    bar_colours = [artist_colour[artist] for artist in list(df.index)]
    ax = df.plot(kind='bar', figsize=[12, 7], width=0.8, alpha=0.7, color=bar_colours, edgecolor=None, zorder=2)
    ax.yaxis.grid(True)
    ax.set_xticklabels(df.index, rotation=45, rotation_mode='anchor', ha='right')
    ax.set_title(f"{end_date.strftime('%b-%Y')}")
    plt.ylim(0, ylimit)
    ax.set_xlabel('')
    ax.set_ylabel('plays')
    plt.savefig(f'{IMG_DIR}/{count}.png', dpi=96, bbox_inches='tight')
    print(f'saved {count}')
    plt.clf()

def set_colors():
        with open('rgb.txt') as f:
                colours = f.readlines()
        return [colour.split('\t')[1] for colour in colours[1:]]

def set_artist_colour(artist):
    choice = random.choice(colours)
    if artist not in artist_colour.keys():
        artist_colour[artist] = choice
        colours.remove(choice)


colours = set_colors()
artist_colour = {}
count = 0
scrobbles = prepare_data()
start_date = scrobbles['timestamp'].min()
to_date = start_date + datetime.timedelta(days=31)
last_day = scrobbles['timestamp'].max()
limit = scrobbles['artist'].value_counts().max()
while to_date < last_day:
    top_20 = total_scrobbles_over_time(scrobbles, to_date)
    artist_list = list(top_20.index)
    for i in artist_list:
        set_artist_colour(i)
    create_bar_chart(top_20, count, to_date, limit)
    count += 1
    to_date += datetime.timedelta(days=31)

