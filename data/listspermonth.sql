WITH artist_lists AS (
SELECT 
	A.name
	,strftime('%Y-%m', DATE(timestamp, 'unixepoch')) AS month_year
	,DATE(timestamp, 'unixepoch') [Date]
	,COUNT(*) AS listen_count
FROM 
	listens AS L
	JOIN tracks AS T on T.id = L.track_id
	JOIN artists AS A ON A.id = T.artist_id
	WHERE DATE(timestamp, 'unixepoch') BETWEEN '2023-12-01' AND '2024-11-30'
GROUP BY month_year, a.name
)

SELECT
    month_year,
    name,
    listen_count
FROM (
    SELECT
        month_year,
        name,
        listen_count,
        RANK() OVER (PARTITION BY month_year ORDER BY listen_count DESC) AS rank
    FROM artist_lists
)
WHERE rank = 1
ORDER BY month_year;
