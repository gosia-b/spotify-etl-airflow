import logging
import sqlite3
from datetime import datetime, timedelta
import pickle

import requests
import pandas as pd
from dateutil import parser
import sqlalchemy
from sqlalchemy.exc import IntegrityError

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


def extract_data() -> None:
    """
    Extract data from Spotify API
    Use API endpoint /me/player/recently-played to get tracks played during the last 24 hours (max 50 tracks!)
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

    with open('dags/api_response.pkl', 'wb') as file:
        pickle.dump(r, file)

    logging.info('Data extracted from Spotify API and saved to api_response.pkl')


def transform_data() -> None:
    """
    Transform API response to a pandas DataFrame with specified columns
    """

    with open('dags/api_response.pkl', 'rb') as file:
        r = pickle.load(file)

    data = pd.json_normalize(r.json()['items'])

    if not data.empty:
        data = pd.DataFrame({
            'played_at': data['played_at'].apply(parser.parse),
            'track_id': data['track.id'],
            'track_name': data['track.name'],
            'album_id': data['track.album.id'],
            'album_name': data['track.album.name'],
            'album_year': data['track.album.release_date'].apply(lambda i: i[:4]),
            'artist_name': data['track.album.artists'].apply(lambda i: i[0]['name']),
            'artist_id': data['track.album.artists'].apply(lambda i: i[0]['id']),
        }).sort_values(by='played_at').reset_index(drop=True)

    with open('dags/data.pkl', 'wb') as file:
        pickle.dump(data, file)

    logging.info('Data transformed and saved to data.pkl')


def load_data() -> None:
    """
    Save data from DataFrame to a database
    """

    with open('dags/data.pkl', 'rb') as file:
        df = pickle.load(file)

    # Connect to the database
    database_location = f'sqlite:///{DATABASE}'
    engine = sqlalchemy.create_engine(database_location)
    con = sqlite3.connect(DATABASE)
    logging.info('Opened database')

    # Create table if needed
    query_create_table = """
    CREATE TABLE IF NOT EXISTS played_tracks(
        played_at TIMESTAMP,
        track_id VARCHAR(200),
        track_name VARCHAR(200),
        album_id VARCHAR(200),
        album_name VARCHAR(200),
        album_year INT(4),
        artist_name VARCHAR(200),
        artist_id VARCHAR(200),
        context VARCHAR(100),
        playlist_id VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )
    """
    with con:
        con.execute(query_create_table)
    logging.info('Table created or already exists')

    # Append dataframe to the database table
    for i, _ in df.iterrows():
        try:
            df.iloc[i:i + 1].to_sql('played_tracks', con=engine, index=False, if_exists='append')
        except IntegrityError:
            pass  # If played_at already exists in the table, don't insert the row
    logging.info('Data successfully saved to a database')
