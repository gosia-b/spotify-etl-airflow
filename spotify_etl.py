import logging
import sqlite3
from datetime import datetime, timedelta

import requests
import pandas as pd
from dateutil import parser
import sqlalchemy

from config import REFRESH_TOKEN, AUTHORIZATION_ENCODED, DATABASE


def get_api_token() -> str:
    """ Generate new API token """
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={'grant_type': 'refresh_token', 'refresh_token': REFRESH_TOKEN},
        headers={'Authorization': f'Basic {AUTHORIZATION_ENCODED}'}
    )
    token = response.json()['access_token']
    return token


def get_headers(token: str) -> dict:
    """ Generate headers for API request """
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    return headers


def get_recently_played() -> pd.DataFrame:
    """
    Use API endpoint /me/player/recently-played to get songs played during the last 24 hours (max 50 songs!)
    API documentation: https://developer.spotify.com/documentation/web-api/reference/#/operations/get-recently-played
    """

    limit = 50  # maximum limit, according to API documentation
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000  # in milliseconds

    # Get data from Spotify API
    url = f'https://api.spotify.com/v1/me/player/recently-played?limit={limit}&after={yesterday_unix_timestamp}'
    token = get_api_token()
    headers = get_headers(token)
    r = requests.get(url, headers=headers)
    data = pd.json_normalize(r.json()['items'])

    song_df = pd.DataFrame({
        'played_at': data['played_at'].apply(parser.parse),
        'song_name': data['track.name'],
        'artist': data['track.album.artists'].apply(lambda i: i[0]['name']),
        'album_name': data['track.album.name'],
        'album_year': data['track.album.release_date'].apply(lambda i: i[:4]),
        'explicit': data['track.explicit'],
        'popularity': data['track.popularity']
    })

    logging.info('Data extracted from Spotify API')
    return song_df


def save_to_database(df: pd.DataFrame) -> None:
    # Connect to the database
    database_location = f'sqlite:///{DATABASE}'
    engine = sqlalchemy.create_engine(database_location)
    con = sqlite3.connect(DATABASE)
    logging.info('Opened database')

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
    with con:
        con.execute(query_create_table)
    logging.info('Table created or already exists')

    # Append dataframe to the database table
    df.to_sql('played_tracks', con=engine, index=False, chunksize=1, if_exists='replace')
    logging.info('Data appended successfully')


def run_spotify_etl() -> None:
    """ Save recently played songs to database """
    df = get_recently_played()
    save_to_database(df)
