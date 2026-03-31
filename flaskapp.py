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
@app.route('/add-song', methods=['GET', 'POST'])
def add_song():
    if request.method == 'POST':
        # Extract and clean form data
        song_title = request.form['song_title'].strip()
        artist = request.form['artist'].strip()
        album_title = request.form['album_title'].strip()
        duration = request.form['duration'].strip()

        # --- Validation ---
        if not song_title:
            flash('Song title cannot be empty!', 'danger')
            return redirect(url_for('add_song'))
        if not artist:
            flash('Artist cannot be empty!', 'danger')
            return redirect(url_for('add_song'))
        if not album_title:
            flash('Album cannot be empty!', 'danger')
            return redirect(url_for('add_song'))
        
        # Validate duration format MM:SS
        import re
        if not re.match(r'^\d{1,2}:\d{2}$', duration):
            flash('Invalid duration format. Use MM:SS.', 'danger')
            return redirect(url_for('add_song'))
        
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
        cursor.execute("""
            INSERT INTO songs (title, duration, artist, album_id)
            VALUES (%s, %s, %s, %s)
        """, (song_title, duration, artist, album_id))
        db.commit()

        flash('Song added successfully! 🎵', 'success')
        return redirect(url_for('home'))
    
    # GET request — just render form
    return render_template('add_song.html')
#Delete a Song
@app.route('/delete-song', methods=['GET', 'POST'])
def delete_song():
    if request.method == 'POST':
        # Use .get() for safety and match the input name
        title = request.form.get('title', '').strip()
        if not title:
            flash('Please enter a song title to delete.', 'danger')
            return redirect(url_for('delete_song'))

        # Delete from DB
        cursor.execute("DELETE FROM songs WHERE title = %s", (title,))
        db.commit()

        flash(f'Song "{title}" deleted successfully!', 'warning')
        return redirect(url_for('home'))
    else:
        return render_template('delete_song.html')

#Display songs
@app.route('/display-songs')
def display_songs():
    # Select songs along with their album titles
    query = """
    SELECT 
        s.song_id, 
        s.title AS song, 
        s.duration, 
        s.artist, 
        a.title AS album
    FROM songs s
    LEFT JOIN albums a ON s.album_id = a.album_id
    ORDER BY s.artist, a.title, s.title;
    """
    cursor.execute(query)
    songs_list = cursor.fetchall()  # returns a list of dicts because cursor is dictionary=True

    # Ensure all fields display correctly, replace None with empty string if needed
    for song in songs_list:
        if song['artist'] is None:
            song['artist'] = ''
        if song['album'] is None:
            song['album'] = ''
        if song['duration'] is None:
            song['duration'] = ''

    return render_template('display_songs.html', songs=songs_list)


# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
