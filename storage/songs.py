from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class addSong(Base):
    """Recieves a song"""

    __tablename__ = "add_song"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), primary_key=False)
    song_length = Column(Integer, nullable=False)
    username = Column(String(250), nullable=False)
    released_date = Column(String(250), nullable=False)
    trace_id = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, name, song_length, username, released_date, trace_id):
        """ Initializes when song is added """
        self.name = name
        self.song_length = song_length
        self.username = username
        self.released_date = released_date
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now()
    
    def to_dict(self):
        """ Dictionary representation when song added"""
        dict = {}
        dict['id'] = self.id
        dict['name'] = self.name
        dict['song_length'] = self.song_length
        dict['username'] = self.username
        dict['released_date'] = self.released_date
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created


        return dict