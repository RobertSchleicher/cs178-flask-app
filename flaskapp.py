# author: T. Urness and M. Moore
# description: Flask example using redirect, url_for, and flash
# credit: the template html files were constructed with the help of ChatGPT
import mysql.connector
import creds  # contains host, user, password, db

db = mysql.connector.connect(
    host=creds.host,
    user=creds.user,
    password=creds.password,
    database=creds.db
)

cursor = db.cursor(dictionary=True)
from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
from dbCode import *

app = Flask(__name__)
app.secret_key = 'your_secret_key' # this is an artifact for using flash displays; 
                                   # it is required, but you can leave this alone
#Home Page
@app.route('/')
def home():
    return render_template('home.html')
#Add a song
# Add a song
@app.route('/add-song', methods=['GET', 'POST'])
def add_song():
    if request.method == 'POST':
        song_title = request.form['song_title']
        artist_names = request.form['artist'].split(',')  # allow multiple artists comma-separated
        album_title = request.form['album_title']
        duration = request.form['duration']

        # --- Handle album ---
        cursor.execute("SELECT album_id FROM albums WHERE title = %s", (album_title,))
        album_result = cursor.fetchone()
        if album_result:
            album_id = album_result['album_id']
        else:
            cursor.execute("INSERT INTO albums (title) VALUES (%s)", (album_title,))
            db.commit()
            album_id = cursor.lastrowid

        # --- Insert song ---
        cursor.execute("INSERT INTO songs (title, duration, album_id) VALUES (%s, %s, %s)",
                       (song_title, duration, album_id))
        db.commit()
        song_id = cursor.lastrowid

        # --- Handle artists ---
        for name in artist_names:
            name = name.strip()
            if not name:
                continue
            # Check if artist exists
            cursor.execute("SELECT artist_id FROM artist WHERE name = %s", (name,))
            artist_result = cursor.fetchone()
            if artist_result:
                artist_id = artist_result['artist_id']
            else:
                cursor.execute("INSERT INTO artist (name) VALUES (%s)", (name,))
                db.commit()
                artist_id = cursor.lastrowid

            # Insert into song_artists
            cursor.execute("INSERT INTO song_artists (song_id, artist_id) VALUES (%s, %s)",
                           (song_id, artist_id))
        db.commit()

        flash('Song added successfully!', 'success')
        return redirect(url_for('home'))

    else:
        return render_template('add_song.html')


# Display songs with all artists
@app.route('/display-songs')
def display_songs():
    query = """
    SELECT s.song_id, s.title AS song, s.duration, a.title AS album,
           GROUP_CONCAT(ar.name SEPARATOR ', ') AS artists
    FROM songs s
    LEFT JOIN albums a ON s.album_id = a.album_id
    LEFT JOIN song_artists sa ON s.song_id = sa.song_id
    LEFT JOIN artist ar ON sa.artist_id = ar.artist_id
    GROUP BY s.song_id
    ORDER BY artists, album, song;
    """
    cursor.execute(query)
    songs_list = cursor.fetchall()
    return render_template('display_songs.html', songs=songs_list)


# Delete a song safely
@app.route('/delete-song', methods=['GET', 'POST'])
def delete_song():
    if request.method == 'POST':
        title = request.form['title']

        # Get song_id(s) first
        cursor.execute("SELECT song_id FROM songs WHERE title = %s", (title,))
        song_rows = cursor.fetchall()
        if not song_rows:
            flash('Song not found.', 'danger')
            return redirect(url_for('delete_song'))

        for row in song_rows:
            song_id = row['song_id']

            # Delete from song_artists first
            cursor.execute("DELETE FROM song_artists WHERE song_id = %s", (song_id,))
            db.commit()

            # Delete from songs
            cursor.execute("DELETE FROM songs WHERE song_id = %s", (song_id,))
            db.commit()

        flash(f'Song "{title}" deleted successfully.', 'warning')
        return redirect(url_for('home'))
    else:
        return render_template('delete_song.html')


# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
