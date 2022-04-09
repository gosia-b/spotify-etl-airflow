from datetime import datetime, timedelta

from spotify_api import get_recently_played


after = datetime(2022, 1, 8)
song_df = get_recently_played(limit=10, after=after, before=after)
print(song_df)
