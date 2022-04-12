import logging
import requests
from datetime import datetime, timedelta

import pandas as pd
from dateutil import parser

from config import REFRESH_TOKEN, AUTHORIZATION_ENCODED


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


def get_last_24h_data():
    limit = 50
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    song_df = get_recently_played(limit=limit, after=yesterday)
    print(song_df)


get_last_24h_data()
