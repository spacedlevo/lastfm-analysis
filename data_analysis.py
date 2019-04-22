import pandas as pd
import pytz
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

def get_colors(cmap, n, start=0., stop=1., alpha=1., reverse=False):
    '''return n-length list of rgba colors from the passed colormap name and alpha,
       limit extent by start/stop values and reverse list order if flag is true'''
    colors = [cm.get_cmap(cmap)(x) for x in np.linspace(start, stop, n)]
    colors = [(r, g, b, alpha) for r, g, b, _ in colors]
    return list(reversed(colors)) if reverse else colors

def create_bar_chart(df, image_title='lastfm-artists-played-most', title='Artists I have played the most'):
    ax = df.plot(kind='bar', figsize=[11, 7], width=0.8, alpha=0.7, color='#B90000', edgecolor=None, zorder=2)
    ax.yaxis.grid(True)
    ax.set_xticklabels(df.index, rotation=45, rotation_mode='anchor', ha='right')
    ax.set_title(f'{title}')
    ax.set_xlabel('')
    ax.set_ylabel('Number of plays')
    plt.savefig(f'images/{image_title}.png', dpi=96, bbox_inches='tight')
    plt.clf()


# Prepare data
scrobbles = pd.read_csv('data/scrobbles.csv')
scrobbles = scrobbles.drop('timestamp', axis=1)
scrobbles['timestamp'] = pd.to_datetime(scrobbles['datetime']) 
scrobbles = scrobbles.drop('datetime', axis=1)
scrobbles = scrobbles.replace(to_replace='Maxïmo Park', value='Maximo Park')
scrobbles = scrobbles[scrobbles['artist'] != 'BBC Radio 4']
scrobbles = scrobbles[scrobbles['artist'] != 'guardian.co.uk']
scrobbles = scrobbles[scrobbles['artist'] != 'cnet.com']

# Convert UTC timestamps to GMT
gmt = pytz.timezone('Europe/London')
scrobbles['timestamp'] = scrobbles['timestamp'].dt.tz_localize(pytz.utc).dt.tz_convert(gmt)

scrobbles['year'] = scrobbles['timestamp'].dt.year
scrobbles['month'] = scrobbles['timestamp'].dt.month
scrobbles['day'] = scrobbles['timestamp'].dt.day
scrobbles['hour'] = scrobbles['timestamp'].dt.hour
scrobbles['dow'] = scrobbles['timestamp'].dt.dayofweek



print(f'Total Scrobbles: {len(scrobbles):,}')
print(f'Total Artists: {len(scrobbles["artist"].unique()):,}')


# scrobbles per year
year_counts = scrobbles['year'].value_counts().sort_index()
ax = year_counts.plot(kind='line', figsize=[10, 5], linewidth=4, alpha=1, marker='o', color='#B90000', 
                      markeredgecolor='#6684c1', markerfacecolor='w', markersize=8, markeredgewidth=2)

ax.set_xlim((year_counts.index[0], year_counts.index[-1]))

ax.yaxis.grid(True)
ax.xaxis.grid(True)
ax.set_ylim(0, 7000)
ax.set_xticks(year_counts.index)
ax.set_ylabel('Number of plays')
ax.set_xlabel('')
ax.set_title('Number of songs played per year')

plt.savefig('images/lastfm-scrobbles-per-year.png', dpi=96, bbox_inches='tight')


# Popular days to scrobble
dow_counts = scrobbles['dow'].value_counts().sort_index()
dow_counts.index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
ax = dow_counts.plot(kind='bar', figsize=[6, 5], width=0.7, alpha=0.6, color='#B90000', edgecolor=None, zorder=2)

ax.yaxis.grid(True)
ax.set_xticklabels(dow_counts.index, rotation=35, rotation_mode='anchor', ha='right')
ax.set_ylim((0, 10000))
ax.set_title('Songs played per day of the week')
ax.set_xlabel('')
ax.set_ylabel('Number of plays')

plt.savefig('images/lastfm-scrobbles-per-weekday.png', dpi=96, bbox_inches='tight')

# Cumlative sum per year of top 5 artists
artists_most = scrobbles['artist'].value_counts()
n = 5
plays = scrobbles[scrobbles['artist'].isin(artists_most.head(n).index)]
plays = plays.groupby(['artist','year']).count().groupby(level=[0]).cumsum()['track']
plays = plays.unstack().T.fillna(method='ffill').T.stack()
top_artists = plays.index.levels[0]

fig, ax = plt.subplots(figsize=[8, 6])
colors = get_colors('Set1', n)
lines = []

for artist, c in zip(top_artists, colors):
    ax = plays[artist].plot(kind='line', linewidth=4, alpha=0.6, marker='o', c=c)
    lines.append(artist)

ax.set_xlim((plays.index.get_level_values(1).min(), plays.index.get_level_values(1).max()))

ax.yaxis.grid(True)
ax.set_xticklabels(plays.index.levels[1], rotation=0, rotation_mode='anchor', ha='center')
ax.set_ylabel('Cumulative number of plays')
ax.set_xlabel('Year')
ax.set_title('Cumulative number of plays per artist over time')
ax.legend(lines, loc='upper right', bbox_to_anchor=(1.33, 1.016))

plt.savefig('images/lastfm-scrobbles-top-artists-years.png', dpi=96, bbox_inches='tight')
plt.clf()

# Analyse top 25 artists Pre and Post 2011
artists_most_25 = artists_most.head(25)
create_bar_chart(artists_most_25)
top_2007_2010 = scrobbles[scrobbles['year'] < 2011]['artist'].value_counts()
create_bar_chart(top_2007_2010.head(25), 'lastfm-top-artists-before-2011', 'Top 25 artists I have listened to before 2011')
top_after_2011 = scrobbles[scrobbles['year'] > 2011]['artist'].value_counts()
create_bar_chart(top_after_2011.head(25), 'lastfm-top-artists-after-2011', 'Top 25 artists I have listened to after 2011')

# compare the pre and post 2011 top artists and makes a list of artist that are new for post 2011
new_entries_vs_pre2011 = [i for i in top_after_2011.head(25).index if i not in top_2007_2010.head(25).index]
new_entries_compared_overall = [i for i in top_after_2011.head(25).index if i in artists_most_25.index]
print(new_entries_compared_overall)
print(len(new_entries_compared_overall))

# find out per year how many artists I listen to
year_on_year = scrobbles.groupby('year')['artist'].nunique()
create_bar_chart(year_on_year, 'lastfm-unqiue-artsists-per-year', "Number of artists listened to per year")

# Find artists that are new to much per year
never_listened_to_df = scrobbles.drop_duplicates(['artist'])
never_listened_to_count = never_listened_to_df.groupby('year')['artist'].size()
create_bar_chart(never_listened_to_count, 'lastfm-new-artist', 'First time I listened to an artist')

# Looking at how many tracks of a particular artists I listen too. 
tracks_per_artist = scrobbles[scrobbles['artist'].isin(artists_most.head(25).index)]
tracks_per_artist = tracks_per_artist.drop_duplicates(['track'])
tracks_per_artist = tracks_per_artist['artist'].value_counts()

ax = tracks_per_artist.sort_values().plot(kind='barh', figsize=[6, 10], width=0.8, alpha=0.6, 
                                    color='#2C3E50', edgecolor=None, zorder=2)
ax.xaxis.grid(True)
ax.set_xlabel('Number of plays')
ax.set_ylabel('')
ax.set_title('Amount of Tracks I have listened to of the top artist', y=1.005)

plt.savefig('images/lastfm-tracks-per-artist-h.png', dpi=96, bbox_inches='tight')
plt.clf()

tracks_per_artist = scrobbles.drop_duplicates(['track'])
tracks_per_artist = tracks_per_artist['artist'].value_counts()

ax = tracks_per_artist.head(25).sort_values().plot(kind='barh', figsize=[6, 10], width=0.8, alpha=0.6, 
                                    color='#DAA520', edgecolor=None, zorder=2)
ax.xaxis.grid(True)
ax.set_xlabel('Number of plays')
ax.set_ylabel('')
ax.set_title('Amount of Tracks I have listened to of all artists', y=1.005)

plt.savefig('images/lastfm-tracks-per-all-artist-h.png', dpi=96, bbox_inches='tight')
