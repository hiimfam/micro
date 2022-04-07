import connexion
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import json
import requests
import datetime
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from stats import Stats
from flask_cors import CORS, cross_origin

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

# Create a basic logger
logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine("sqlite:///stats.sqlite")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_stats():
    """ Receives artist and song readings processed statistics """

    session = DB_SESSION()
    stats = session.query(Stats).order_by(Stats.last_updated.desc()).first()
  
    if stats:
        return stats.to_dict(), 200
    return {"message":"No stats found"}, 400


def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")
    last_updated = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    session = DB_SESSION()
    latest_stats = session.query(Stats).order_by(Stats.last_updated.desc()).first()

    if latest_stats:
        latest_stats = latest_stats.to_dict()
    else:
        latest_stats = {
            "num_artist_readings": 1,
            "max_albums_recorded_reading": 0,
            "max_song_length_reading": 0,
            "num_song_readings": 1,
            "last_updated": last_updated
        }

    session.close()

    new_stats = latest_stats
    timestamp = stats["last_updated"]
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    end_timestamp = current_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    response = requests.get('http://localhost:8090/artists' + '?start_timestamp=' + start_timestamp + "&end_timestamp=" + end_timestamp)

    if response and response.status_code == 200:
        if len(response.json()) != 0:
            logging.info(f'Return {len(response.json())} numbers of events')
            albums_recorded_result = []
            for report in response.json(): 
                albums_recorded_result.append(report)
                new_stats["max_albums_recorded_reading"] = max(new_stats["max_albums_recorded_reading"], report["albums_recorded"])
                logging.debug(f'Process albums recorded event with trace id: {report["trace_id"]}')

            new_stats["num_artist_readings"] = latest_stats["num_artist_readings"] + len(albums_recorded_result)

    else:
        logging.error(f'Albums recorded response failed with {response.status_code}')

    response = requests.get('http://localhost:8090/songs' + '?start_timestamp=' + start_timestamp + "&end_timestamp=" + end_timestamp)

    if response and response.status_code == 200:
        if len(response.json()) != 0:
            logging.info(f'Return {len(response.json())} numbers of events')
            song_length_result = []
            for report in response.json(): 
                song_length_result.append(report)
                new_stats["max_song_length_reading"] = max(new_stats["max_song_length_reading"], report["song_length"])
                logging.debug(f'Process song length event with trace id: {report["trace_id"]}')

            new_stats["num_song_readings"] = latest_stats["num_song_readings"] + len(song_length_result)
    else:
        logging.error(f'Song length response failed with {response.status_code}')

    new_stats["last_updated"] = datetime.datetime.now()
    logging.debug(new_stats)
    session = DB_SESSION()

    stat = Stats(new_stats["num_artist_readings"],
                  new_stats["max_albums_recorded_reading"],
                  new_stats["max_song_length_reading"],
                  new_stats["num_song_readings"],
                  new_stats["last_updated"])

    session.add(stat)

    session.commit()
    session.close()

    logging.debug(f'Updated stat: {new_stats}')
    logging.info(f'End Periodic Processing')


def init_scheduler(): 
    sched = BackgroundScheduler(daemon=True) 
    sched.add_job(populate_stats,    
                  'interval', 
                  seconds=app_config['scheduler']['period_sec']) 
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__": 
    init_scheduler()
    app.run(port=8100, use_reloader=False)
