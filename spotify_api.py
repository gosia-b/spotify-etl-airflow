import logging
import requests
from datetime import datetime

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


def get_headers(token):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    return headers


def date_to_unix_timestamp_milliseconds(date: datetime) -> int:
    return int(date.timestamp()) * 1000


def get_recently_played(limit: int, after: datetime, before: datetime) -> pd.DataFrame:
    """
    Documentation: https://developer.spotify.com/documentation/web-api/reference/#/operations/get-recently-played

    Returns:
        Tracks from the current user's recently played tracks, in a form of pandas DataFrame with the following columns:
        - played_at
        - song_name
        - artist
        - album_name
        - album_year
    """

    after = date_to_unix_timestamp_milliseconds(after)

    # Get data from Spotify API
    url = f"https://api.spotify.com/v1/me/player/recently-played?limit={limit}&after={after}"
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

    for song in data["items"]:
        played_at.append(parser.parse(song["played_at"]))
        song_name.append(song["track"]["name"])
        artist.append(song["track"]["album"]["artists"][0]["name"])
        album_name.append(song["track"]["album"]["name"])
        album_year.append(song["track"]["album"]["release_date"][:4])

    song_dict = {
        "played_at": played_at,
        "song_name": song_name,
        "artist": artist,
        "album_name": album_name,
        "album_year": album_year
    }

    song_df = pd.DataFrame(song_dict)
    logging.info("Data extracted from Spotify API")

    return song_df
