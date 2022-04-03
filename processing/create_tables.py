import sqlite3

conn = sqlite3.connect('stats.sqlite')

c = conn.cursor()
c.execute(''' 
          CREATE TABLE stats
          (id INTEGER PRIMARY KEY ASC,
           num_artist_readings INTEGER NOT NULL, 
           max_albums_recorded_reading INTEGER,
           max_song_length_reading INTEGER,
           num_song_readings INTEGER NOT NULL,
           last_updated VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()