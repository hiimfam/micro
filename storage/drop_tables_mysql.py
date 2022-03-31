import mysql.connector


db_conn = mysql.connector.connect(host="william-micro.eastus2.cloudapp.azure.com", user="root", password="Epicfaildance1!", database="events")

db_cursor = db_conn.cursor()


db_cursor.execute('''
          DROP TABLE add_artist, add_song
          ''')

db_conn.commit()
db_conn.close()