from datetime import datetime, timedelta

from spotify_api import get_recently_played


limit = 50
after = datetime(2022, 1, 8)
song_df = get_recently_played(limit=limit, after=after)
print(song_df)
