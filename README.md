# Overview
Collect your history of songs played on Spotify in a database.  
Spotify API allows to get only 50 recently played tracks so in this project I use Airflow to collect the data daily and save it to a SQLite database.  

<img src="https://github.com/gosia-b/spotify-etl-airflow/blob/master/spotify-etl-airflow.drawio.png">

The data is saved to a database table `played_tracks`. Here is how an example row looks like:
<br><br>
<img src="https://github.com/gosia-b/spotify-etl-airflow/blob/master/example_row.png">

# Prerequisites
- Airflow installed
- Spotify account

# Further work
The database table created contains IDs of tracks, albums, artists and playlists. This allows to gather data from other API endpoints like Get Track or Get Artist to do interesting analyses.

# Reference
Based on videos [1](https://www.youtube.com/watch?v=dvviIUKwH7o), [2](https://www.youtube.com/watch?v=X-phMpEp6Gs),
[3](https://www.youtube.com/watch?v=rvPtpOjzVTQ), [4](https://www.youtube.com/watch?v=i25ttd32-eo)  
[Airflow quick start](https://airflow.apache.org/docs/apache-airflow/stable/start/local.html)  
[How to run Airflow on Windows](https://dev.to/jfhbrook/how-to-run-airflow-on-windows-with-docker-2d01)  
