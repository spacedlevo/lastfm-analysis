import sqlite3
import pandas as pd
import seaborn as sns
import numpy as np
import calendar
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Connect to the database
conn = sqlite3.connect("/home/levo/Documents/projects/lastfm/data/lastfmscrobbles.db")
YEAR = "2025"
# Query the database
query = """
SELECT
    a.name [artist]
    ,t.name [track]
    ,al.name [album]
    ,timestamp
    ,date(timestamp, 'unixepoch') AS list_date
    ,time(timestamp, 'unixepoch') AS listen_time
    ,strftime('%m', datetime(timestamp, 'unixepoch')) [Month]
    ,strftime('%Y', datetime(timestamp, 'unixepoch')) [Year]
	,strftime('%j', date(timestamp, 'unixepoch')) [day of year]
FROM 
    listens AS l
JOIN tracks AS t ON t.id = l.track_id
JOIN artists AS a ON a.id = t.artist_id
JOIN albums AS al ON al.id = t.album_id
ORDER BY timestamp DESC
"""

df = pd.read_sql_query(query, conn)
df["timestamp"] = pd.to_datetime(df["list_date"])


# Close the connection
conn.close()


def create_heatmap(year):
    # Convert timestamp to datetime
    heatmap_df = df[df["Year"] == year]

    # Extract day and month
    heatmap_df["day"] = heatmap_df["timestamp"].dt.day
    heatmap_df["month"] = heatmap_df["timestamp"].dt.month

    # Create a pivot table with counts of listens per day
    heatmap_data = heatmap_df.pivot_table(
        index="month", columns="day", aggfunc="size", fill_value=0
    )

    # Ensure the heatmap has 31 days and 12 months
    heatmap_data = heatmap_data.reindex(
        index=np.arange(1, 13), columns=np.arange(1, 32), fill_value=0
    )
    # Create a custom colormap with more colors
    colors = ["#07101A", "#1E3A5F", "#3A6BAA", "#469DF8", "#7FB3F5", "#B3D7FF"]
    cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)

    # Plot the heatmap
    plt.figure(figsize=(12, 4))  # Increased height by 50 pixels
    sns.heatmap(heatmap_data, cmap=cmap, linewidths=0.1, linecolor="gray", cbar=True)
    plt.title(f"Daily Listens Heatmap for {YEAR}")
    plt.xlabel("Day")
    plt.ylabel("Month")
    plt.yticks(
        ticks=np.arange(0.5, 12.5),
        labels=[calendar.month_abbr[i] for i in range(1, 13)],
    )
    plt.savefig("heatmap.png")


def scrobbles_to_date():
    # Convert timestamp to datetime

    # Filter data for the current year and the previous year
    current_year_data = df[df["Year"] == str(int(YEAR))]
    previous_year_data = df[df["Year"] == str(int(YEAR) - 1)]

    # Calculate the number of tracks listened to up to today's date in the current year
    current_year_count = current_year_data[
        current_year_data["timestamp"].dt.dayofyear <= pd.Timestamp.now().dayofyear
    ].shape[0]

    # Calculate the number of tracks listened to up to today's date in the previous year
    previous_year_count = previous_year_data[
        previous_year_data["timestamp"].dt.dayofyear <= pd.Timestamp.now().dayofyear
    ].shape[0]

    print(f"Tracks listened to this year ({YEAR}): {current_year_count}")
    print(f"Tracks listened to last year ({int(YEAR) - 1}): {previous_year_count}")


def monthly_comparison_chart():
    # Filter data for the years 2024 and 2025
    data_2024 = df[df["Year"] == "2024"]
    data_2025 = df[df["Year"] == "2025"]

    # Group by month and count the number of tracks listened to each month
    monthly_counts_2024 = data_2024.groupby("Month").size()
    monthly_counts_2025 = data_2025.groupby("Month").size()

    # Create a DataFrame for plotting
    monthly_counts = pd.DataFrame(
        {"2024": monthly_counts_2024, "2025": monthly_counts_2025}
    ).fillna(0)

    # Plot the bar chart
    monthly_counts.plot(kind="bar", figsize=(8.5, 2))
    plt.title("Monthly Listens Comparison: 2024 vs 2025")
    plt.xlabel("Month")
    plt.ylabel("Number of Listens")
    plt.xticks(
        ticks=np.arange(12),
        labels=[calendar.month_abbr[i] for i in range(1, 13)],
        rotation=0,
    )
    plt.legend(title="Year", bbox_to_anchor=(1, 1), loc="upper left", borderaxespad=0.0)
    plt.savefig("monthly_comparison_chart.png")


def stacked_bar_charts():
    # Filter data for the years 2024 and 2025
    data_2024 = df[df["Year"] == "2024"]
    data_2025 = df[df["Year"] == "2025"]

    # Group by month and count the number of artists, albums, and tracks listened to each month
    monthly_artists_2024 = data_2024.groupby("Month")["artist"].nunique()
    monthly_artists_2025 = data_2025.groupby("Month")["artist"].nunique()
    monthly_albums_2024 = data_2024.groupby("Month")["album"].nunique()
    monthly_albums_2025 = data_2025.groupby("Month")["album"].nunique()
    monthly_tracks_2024 = data_2024.groupby("Month")["track"].nunique()
    monthly_tracks_2025 = data_2025.groupby("Month")["track"].nunique()

    # Create DataFrames for plotting
    artists_counts = pd.DataFrame(
        {"2024": monthly_artists_2024, "2025": monthly_artists_2025}
    ).fillna(0)
    albums_counts = pd.DataFrame(
        {"2024": monthly_albums_2024, "2025": monthly_albums_2025}
    ).fillna(0)
    tracks_counts = pd.DataFrame(
        {"2024": monthly_tracks_2024, "2025": monthly_tracks_2025}
    ).fillna(0)

    # Plot the bar charts
    fig, axes = plt.subplots(3, 1, figsize=(8.5, 6), sharex=True)

    artists_counts.plot(
        kind="bar", ax=axes[0], color=["#1f77b4", "#ff7f0e"], legend=False
    )
    axes[0].set_title("Monthly Unique Artists Comparison: 2024 vs 2025")
    axes[0].set_ylabel("Number of Artists")

    albums_counts.plot(
        kind="bar", ax=axes[1], color=["#1f77b4", "#ff7f0e"], legend=False
    )
    axes[1].set_title("Monthly Unique Albums Comparison: 2024 vs 2025")
    axes[1].set_ylabel("Number of Albums")

    tracks_counts.plot(kind="bar", ax=axes[2], color=["#1f77b4", "#ff7f0e"])
    axes[2].set_title("Monthly Unique Tracks Comparison: 2024 vs 2025")
    axes[2].set_ylabel("Number of Tracks")
    axes[2].set_xlabel("Month")
    axes[2].set_xticks(np.arange(12))
    axes[2].set_xticklabels([calendar.month_abbr[i] for i in range(1, 13)], rotation=0)

    plt.tight_layout()
    plt.savefig("stacked_bar_charts.png")


def top_5_table(year):
    # Filter data for the specified year
    year_data = df[df["Year"] == year]

    # Get top 5 artists
    top_artists = (
        year_data["artist"]
        .value_counts()
        .head(5)
        .reset_index()
        .rename(columns={"index": "Artist", "artist": "Count"})
    )

    # Get top 5 albums
    top_albums = (
        year_data["album"]
        .value_counts()
        .head(5)
        .reset_index()
        .rename(columns={"index": "Album", "album": "Count"})
    )

    # Get top 5 tracks
    top_tracks = (
        year_data["track"]
        .value_counts()
        .head(5)
        .reset_index()
        .rename(columns={"index": "Track", "track": "Count"})
    )

    # Calculate grand totals
    total_artists = year_data["artist"].value_counts().sum()
    total_albums = year_data["album"].value_counts().sum()
    total_tracks = year_data["track"].value_counts().sum()

    # Add grand totals to the tables
    top_artists.loc[len(top_artists)] = ["Total", total_artists]
    top_albums.loc[len(top_albums)] = ["Total", total_albums]
    top_tracks.loc[len(top_tracks)] = ["Total", total_tracks]

    # Print the tables
    print("Top 5 Artists:")
    print(top_artists)
    print("\nTop 5 Albums:")
    print(top_albums)
    print("\nTop 5 Tracks:")
    print(top_tracks)

    # Save the tables to CSV files
    top_artists.to_csv("top_5_artists.csv", index=False)
    top_albums.to_csv("top_5_albums.csv", index=False)
    top_tracks.to_csv("top_5_tracks.csv", index=False)


def quick_facts(year):
    # Filter data for the specified year
    year_data = df[df["Year"] == year]

    # Calculate total days and hours listened to music
    total_days = year_data["list_date"].nunique()
    total_hours = year_data["timestamp"].dt.hour.sum()

    # Calculate average listens per day
    average_listens_per_day = year_data.shape[0] / total_days

    # Calculate the longest streak of days listened to music
    year_data["day_of_year"] = year_data["timestamp"].dt.dayofyear
    streaks = year_data["day_of_year"].diff().ne(1).cumsum()
    longest_streak = streaks.value_counts().max()

    # Find the day with the most listens
    most_active_day = year_data["list_date"].value_counts().idxmax()
    most_active_day_count = year_data["list_date"].value_counts().max()

    print(f"Total days listened to music in {year}: {total_days}")
    print(f"Total hours listened to music in {year}: {total_hours}")
    print(f"Average listens per day in {year}: {average_listens_per_day:.2f}")
    print(f"Longest streak of days listened to music in {year}: {longest_streak} days")
    print(
        f"Most active day in {year}: {most_active_day} with {most_active_day_count} listens"
    )


quick_facts(YEAR)

top_5_table(YEAR)
stacked_bar_charts()
monthly_comparison_chart()
create_heatmap(YEAR)
scrobbles_to_date()
