SELECT
	a.name [artist]
	,t.name [track]
	,al.name [album]
	,timestamp
    ,date(timestamp, 'unixepoch') AS list_date
	,time(timestamp, 'unixepoch') AS listen_time
	,strftime('%m', datetime(timestamp, 'unixepoch')) [Month]
FROM 
    listens AS l
	JOIN tracks AS t ON t.id = l.track_id
	JOIN artists AS a ON a.id = t.artist_id
	JOIN albums AS al ON al.id = t.album_id
WHERE
    strftime('%Y', datetime(timestamp, 'unixepoch')) = '2025'