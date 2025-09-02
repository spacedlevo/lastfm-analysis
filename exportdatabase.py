import sqlite3
import csv

# Connect to the SQLite database
conn = sqlite3.connect("/home/levo/Documents/projects/lastfm/data/lastfmscrobbles.db")
cursor = conn.cursor()

# Query to join listens, tracks, albums, and artists tables
query = """
SELECT 
    listens.track_id,
    listens.timestamp,
    tracks.name AS track_name,
    albums.name AS album_name,
    artists.name AS artist_name,
    datetime(listens.timestamp, 'unixepoch') AS listen_date,
    strftime('%Y', datetime(listens.timestamp, 'unixepoch')) AS year,
    strftime('%m', datetime(listens.timestamp, 'unixepoch')) AS month,
    strftime('%d', datetime(listens.timestamp, 'unixepoch')) AS day,
    strftime('%H', datetime(listens.timestamp, 'unixepoch')) AS hour,
    strftime('%M', datetime(listens.timestamp, 'unixepoch')) AS minute,
    strftime('%S', datetime(listens.timestamp, 'unixepoch')) AS second
FROM listens
JOIN tracks ON listens.track_id = tracks.id
JOIN albums ON tracks.album_id = albums.id
JOIN artists ON tracks.artist_id = artists.id
"""

# Execute the query
cursor.execute(query)
rows = cursor.fetchall()

# Define the CSV file name
csv_file = "music_listens_export.csv"

# Write the data to a CSV file
with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(
        [
            "track_id",
            "timestamp",
            "track_name",
            "album_name",
            "artist_name",
            "listen_date",
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
        ]
    )
    # Write the data
    writer.writerows(rows)

# Close the database connection
conn.close()

print(f"Data exported to {csv_file}")
