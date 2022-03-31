import mysql.connector

db_conn = mysql.connector.connect(host="william-micro.eastus2.cloudapp.azure.com", user="root", password="Epicfaildance1!", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE add_artist
          (id INT NOT NULL AUTO_INCREMENT,
           artist_id VARCHAR(250) NOT NULL, 
           artist_name VARCHAR(250) NOT NULL,
           username VARCHAR(250) NOT NULL,
           albums_recorded INT(250) NOT NULL,
           trace_id VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT addartist_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE add_song
          (id INT NOT NULL AUTO_INCREMENT,
           name VARCHAR(250) NOT NULL, 
           song_length INT(250) NOT NULL,
           username VARCHAR(100) NOT NULL,
           released_date VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT addsong_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()