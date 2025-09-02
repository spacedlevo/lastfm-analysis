WITH MonthlyDistinctSongs AS (
    SELECT 
        strftime('%Y-%m', timestamp, 'unixepoch') AS month_year,  -- Get Year-Month from the timestamp
        a.name AS artist_name,
        COUNT(DISTINCT t.id) AS distinct_song_count  -- Count distinct songs listened to per artist
    FROM listens l
    JOIN tracks t ON l.track_id = t.id            -- Join listens to tracks
    JOIN artists a ON t.artist_id = a.id           -- Join tracks to artists
    WHERE l.timestamp >= strftime('%s', 'now', '-12 months')  -- Filter listens from the last 12 months
    GROUP BY month_year, artist_name              -- Group by month and artist
)

SELECT
    month_year,
    artist_name,
    distinct_song_count
FROM (
    SELECT
        month_year,
        artist_name,
        distinct_song_count,
        RANK() OVER (PARTITION BY month_year ORDER BY distinct_song_count DESC) AS rank
    FROM MonthlyDistinctSongs
)
WHERE rank = 1
ORDER BY month_year;
