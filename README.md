# Overview
Collect your history of songs played on Spotify in a database.  
Spotify API allows to get only 50 recently played tracks so in this project I use Airflow to collect the data daily and save it to a local SQLite database.  

<img src="https://github.com/gosia-b/spotify-etl-airflow/blob/master/spotify-etl-airflow.drawio.png">

The data is saved to a database table `played_tracks`. Here is how an example row looks like:
<br><br>
<img src="https://github.com/gosia-b/spotify-etl-airflow/blob/master/example_row.png">

# Prerequisites
### 1. Airflow  
How to install Airflow with Docker: [link](https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html)

After installation, in your `docker-compose.yaml` file you need to create a volume so that the folder `dags` is shared between your computer and the Airflow Docker container:
```
volumes:
  - [local path to dags folder]:/opt/airflow/dags
```
### 2. Spotify account
First you need to have a Spotify account  
For API authorization, you need `client_id`, `client_secret` and `refresh_token` - how to get them: [link](https://benwiz.com/blog/create-spotify-refresh-token/)


### 3. File config.py

You need to create a file `dags/config.py` (not included in this repo because it's in `.gitignore`) whith the following constants:
```python
REFRESH_TOKEN = ''
AUTHORIZATION_ENCODED = '' 
DATABASE = 'dags/spotify_db.sqlite'
```
Replace empty `REFRESH_TOKEN` with your `refresh_token` and `AUTHORIZATION_ENCODED` with a string created e.g. this way in Python:
```python
import base64

base64.b64encode(bytes(f"{client_id}:{client_secret}", "ISO-8859-1")).decode("ascii")
```

# Code
https://developer.spotify.com/documentation/web-api/reference/#/operations/get-recently-played

# Further work
The database table created contains IDs of tracks, albums, artists and playlists. This allows to gather data from other API endpoints like Get Track or Get Artist to do interesting analyses.

# Reference
Based on videos [1](https://www.youtube.com/watch?v=dvviIUKwH7o), [2](https://www.youtube.com/watch?v=X-phMpEp6Gs),
[3](https://www.youtube.com/watch?v=rvPtpOjzVTQ), [4](https://www.youtube.com/watch?v=i25ttd32-eo)
