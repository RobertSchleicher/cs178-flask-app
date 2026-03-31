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
        # Extract form data
        song_title = request.form['song_title']
        artist = request.form['artist']
        album_title = request.form['album_title']
        duration = request.form['duration']
        
        # Process the data (e.g., add it to a database)
        # For now, let's just print it to the console
        print("Song Title:", song_title)
        print("Duration:", duration)
        print("Artist:", artist)
        print("Album:", album_title)
        
        flash('Song added successfully! Huzzah!', 'success')  # 'success' is a category; makes a green banner at the top
        # Redirect to home page or another page upon successful submission
        return redirect(url_for('home'))
    else:
        # Render the form page if the request method is GET
        return render_template('add_song.html')
#Delete a Song
@app.route('/delete-song',methods=['GET', 'POST'])
def delete_song():
    if request.method == 'POST':
        # Extract form data
        name = request.form['name']
        
        # Process the data (e.g., add it to a database)
        # For now, let's just print it to the console
        print("Song Title to delete:", name)
        
        flash('Song deleted successfully! Hoorah!', 'warning') 
        # Redirect to home page or another page upon successful submission
        return redirect(url_for('home'))
    else:
        # Render the form page if the request method is GET
        return render_template('delete_song.html')

#Display songs
@app.route('/display-songs')
def display_songs():
    # hard code a value to the songs_list;
    # note that this could have been a result from an SQL query :) 
    query="""
    SELECT song_id, title AS song, duration, artist, album
    FROM songs
    ORDER BY artist, album, title;
    """
    cursor.execute(query)
    songs_list = cursor.fetchall()
    return render_template('display_songs.html', songs = songs_list)


# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
