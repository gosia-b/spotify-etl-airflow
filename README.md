# Motivation
I'd like to collect my Spotify history for analysis. Unfortunately, the Spotify API allows to get only 50 recently played tracks.
So in this project I use Airflow to daily collect data from the previous day and save it to a SQLite database.  

<p align="center">
<img width=70% src="https://github.com/gosia-b/spotify-etl-airflow/blob/master/image.png">
</p>

# Reference
Based on videos [1](https://www.youtube.com/watch?v=dvviIUKwH7o), [2](https://www.youtube.com/watch?v=X-phMpEp6Gs),
[3](https://www.youtube.com/watch?v=rvPtpOjzVTQ), [4](https://www.youtube.com/watch?v=i25ttd32-eo)  
[Airflow quick start](https://airflow.apache.org/docs/apache-airflow/stable/start/local.html)  
[How to run Airflow on Windows](https://dev.to/jfhbrook/how-to-run-airflow-on-windows-with-docker-2d01)  
