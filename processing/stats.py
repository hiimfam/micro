from sqlalchemy import Column, Integer, String, DateTime
from base import Base


class Stats(Base):
    """ Processing Statistics """

    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    num_artist_readings = Column(Integer, nullable=False)
    max_albums_recorded_reading = Column(Integer, nullable=True)
    max_song_length_reading = Column(Integer, nullable=True)
    num_song_readings = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False)


    def __init__(self, num_artist_readings, max_albums_recorded_reading, max_song_length_reading, num_song_readings, last_updated):
        """ Initializes a processing statistics object """
        self.num_artist_readings = num_artist_readings
        self.max_albums_recorded_reading = max_albums_recorded_reading
        self.max_song_length_reading = max_song_length_reading
        self.num_song_readings = num_song_readings
        self.last_updated = last_updated


    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['num_artist_readings'] = self.num_artist_readings
        dict['max_albums_recorded_reading'] = self.max_albums_recorded_reading
        dict['max_song_length_reading'] = self.max_song_length_reading
        dict['num_song_readings'] = self.num_song_readings
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%SZ")

        return dict