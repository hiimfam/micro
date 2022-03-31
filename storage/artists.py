from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class addArtist(Base):
    """Recieves an artist"""

    __tablename__ = "add_artist"
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, primary_key=False)
    artist_name = Column(String(250), nullable=False)
    username = Column(String(250), nullable=False)
    albums_recorded = Column(Integer, nullable=False)
    trace_id = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, artist_id, artist_name, username, albums_recorded, trace_id):
        """ Initializes when artist is added """
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.username = username
        self.albums_recorded = albums_recorded
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now()
    
    def to_dict(self):
        """ Dictionary representation when artist added"""
        dict = {}
        dict['id'] = self.id
        dict['artist_id'] = self.artist_id
        dict['artist_name'] = self.artist_name
        dict['username'] = self.username
        dict['albums_recorded'] = self.albums_recorded
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created


        return dict