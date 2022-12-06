# Overview
Collect your history of songs played on Spotify in a database.  
Spotify API allows to get only 50 recently played tracks so in this project I use Airflow to collect the data daily and save it to a local SQLite database.  

<img src="https://github.com/gosia-b/spotify-etl-airflow/blob/master/images/spotify-etl-airflow.drawio.png">

The data is saved to a database table `played_tracks`. Here is how an example record looks like:
<br><br>
<img src="https://github.com/gosia-b/spotify-etl-airflow/blob/master/images/example_row.png">

# Prerequisites
### 1. Airflow  
How to install Airflow with Docker: [link](https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html)

After installation, in your `docker-compose.yaml` file create a volume so that the folder `dags` is shared between your computer and the Airflow Docker container:
```
volumes:
  - [local path to dags folder]:/opt/airflow/dags
```
### 2. Spotify account
First you need to have a Spotify account.  
For API authorization, you need `client_id`, `client_secret` and `refresh_token` - how to get them: [link](https://benwiz.com/blog/create-spotify-refresh-token/)


### 3. File config.py

Create a file `dags/config.py` (not included in this repo because it's in .gitignore) with the following constants:
```python
REFRESH_TOKEN = ''
AUTHORIZATION_ENCODED = '' 
DATABASE = 'dags/spotify_db.sqlite'
```
Replace empty `REFRESH_TOKEN` with your `refresh_token` and `AUTHORIZATION_ENCODED` with a string created e.g. this way in Python:
```python
import base64

base64.b64encode(bytes(f'{client_id}:{client_secret}', 'ISO-8859-1')).decode('ascii')
```

# Pipeline
The code in `dags/spotify_etl.py` uses Spotify API endpoint Get Recently Played Tracks ([documentation](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-recently-played)) to get your 50 recently played tracks.

A simple Airflow DAG is created in file `dags/spotify_dag.py`. It's set to run daily at midnight and consists of 3 operators - extract, tranform and load:

<img src="https://github.com/gosia-b/spotify-etl-airflow/blob/master/images/pipeline.png" width=40%>

Ouput files:
- operator `extract` creates a file `api_response.pkl` which is used by operator `transform`
- operator `transform` creates a file `data.pkl` which is used by operator `load`

# Further work
The created database table contains IDs of tracks, albums, and artists. This allows to gather data from other API endpoints like Get Track or Get Artist to do interesting analyses.

# Reference
Based on videos [1](https://www.youtube.com/watch?v=dvviIUKwH7o), [2](https://www.youtube.com/watch?v=X-phMpEp6Gs),
[3](https://www.youtube.com/watch?v=rvPtpOjzVTQ), [4](https://www.youtube.com/watch?v=i25ttd32-eo)  
[Spotify API documentation](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-recently-played)
