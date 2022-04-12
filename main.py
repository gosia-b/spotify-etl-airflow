import logging
import sqlite3

import requests
from datetime import datetime, timedelta

import pandas as pd
from dateutil import parser
import sqlalchemy

from config import REFRESH_TOKEN, AUTHORIZATION_ENCODED, DATABASE


def refresh_token() -> str:
    """ Generate new API token """
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
        headers={"Authorization": f"Basic {AUTHORIZATION_ENCODED}"}
    )

    token = response.json()["access_token"]
    return token


def get_headers(token: str) -> dict:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    return headers


def get_recently_played(limit: int, after: datetime) -> pd.DataFrame:
    """
    Documentation: https://developer.spotify.com/documentation/web-api/reference/#/operations/get-recently-played
    Returns a DataFrame with tracks played between "after" and "before" datetime
    """

    after_unix_timestamp = int(after.timestamp()) * 1000  # in milliseconds

    # Get data from Spotify API
    url = f"https://api.spotify.com/v1/me/player/recently-played?limit={limit}&after={after_unix_timestamp}"
    token = refresh_token()
    headers = get_headers(token)
    r = requests.get(url, headers=headers)
    data = r.json()

    # Convert response: JSON to pandas DataFrame
    played_at = []
    song_name = []
    artist = []
    album_name = []
    album_year = []
    explicit = []
    popularity = []

    for song in data["items"]:
        played_at.append(parser.parse(song["played_at"]))
        song_name.append(song["track"]["name"])
        artist.append(song["track"]["album"]["artists"][0]["name"])
        album_name.append(song["track"]["album"]["name"])
        album_year.append(song["track"]["album"]["release_date"][:4])
        explicit.append(song["track"]["explicit"])
        popularity.append(song["track"]["popularity"])

    song_dict = {
        "played_at": played_at,
        "song_name": song_name,
        "artist": artist,
        "album_name": album_name,
        "album_year": album_year,
        "explicit": explicit,
        "popularity": popularity
    }

    song_df = pd.DataFrame(song_dict)

    logging.info("Data extracted from Spotify API")

    return song_df


def save_to_database(df: pd.DataFrame) -> None:
    # Connect to the database
    database_location = f"sqlite:///{DATABASE}"
    engine = sqlalchemy.create_engine(database_location)
    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()
    logging.info("Opened database successfully")

    # Create table if needed
    query_create_table = """
    CREATE TABLE IF NOT EXISTS played_tracks(
        played_at TIMESTAMP,
        song_name VARCHAR(200),
        artist VARCHAR(200),
        album_name VARCHAR(200),
        album_year INT(4),
        explicit BOOL,
        popularity INT(3),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )
    """
    cursor.execute(query_create_table)
    logging.info("Table created or already exists")

    # Append dataframe to the database table
    for i, _ in df.iterrows():
        try:
            df.iloc[i:i + 1].to_sql("played_tracks", con=engine, index=False, if_exists="append")
        except sqlalchemy.exc.IntegrityError:
            pass  # If played_at already exists in the table, don't insert the row


def get_last_24h_data() -> pd.DataFrame:
    limit = 50
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    song_df = get_recently_played(limit=limit, after=yesterday)
    return song_df


def save_last_24h_data_to_database() -> None:
    df = get_last_24h_data()
    save_to_database(df)
