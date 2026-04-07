# author: Robert Schleicher
# description: Flask app using redirect, url_for, request, flash, and render_template to create a simple music library that incorporates mysql and dynamodb. 
# Includes the use of CRUD operations. 
# credit: Html templates were adapted from template with use of ChatGPT. Some of the app route code had help from ChatGPT but the decisions on how to implement was mine.
import mysql.connector
import boto3
import creds  # contains host, user, password, db, aws_access_key, aws_secret_key
from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
from dbCode import *

# MySQL connection
db = mysql.connector.connect(
    host=creds.host,
    user=creds.user,
    password=creds.password,
    database=creds.db
)

cursor = db.cursor(dictionary=True)

# DynamoDB connection
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=creds.aws_access_key,
    aws_secret_access_key=creds.aws_secret_key,
    region_name='us-east-1'
)
dynamo_table = dynamodb.Table('song_stats')



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
        song_title = request.form['song_title']
        artist = request.form['artist']
        album_title = request.form['album_title']

        #Checking for empty fields
        if not song_title:
            flash('Song title cannot be empty!', 'danger')
            return redirect(url_for('add_song'))
        if not artist:
            flash('Artist cannot be empty!', 'danger')
            return redirect(url_for('add_song'))
        if not album_title:
            flash('Album cannot be empty!', 'danger')
            return redirect(url_for('add_song'))
        
        # To connect songs to album using album id. ChatGpt assisted with this with syntax.
        cursor.execute("SELECT album_id FROM albums WHERE title = %s", (album_title,))
        album_result = cursor.fetchone()
        if album_result:
            album_id = album_result['album_id']
        else:
            cursor.execute("INSERT INTO albums (title) VALUES (%s)", (album_title,))
            db.commit()
            album_id = cursor.lastrowid
        
        # Insert song
        cursor.execute("""
            INSERT INTO songs (title, artist, album_id)
            VALUES (%s, %s, %s)
        """, (song_title, artist, album_id))
        db.commit()

        flash('Song added successfully!', 'success')
        return redirect(url_for('home'))
    
    # Render the form page if request method is GET
    return render_template('add_song.html')
#Delete a Song
@app.route('/delete-song', methods=['GET', 'POST'])
def delete_song():
    if request.method == 'POST':
        title = request.form.get('title', '')
        if not title:
            flash('Please enter a song title to delete.', 'danger')
            return redirect(url_for('delete_song'))
        #Chat assited with try except syntax. 
        try:
            # Delete song
            cursor.execute("DELETE FROM songs WHERE title = %s", (title,))
            db.commit()

            flash(f'Song(s) "{title}" and related artist links deleted successfully!', 'warning')

        except mysql.connector.Error as err:
            flash(f'Error deleting song: {err}', 'danger')

        return redirect(url_for('display_songs'))

    return render_template('delete_song.html')

#Update Song
@app.route('/update-song', methods=['GET', 'POST'])
def update_song():
    if request.method == 'POST':
        song_id = request.form.get('song_id')
        new_title = request.form.get('title', '')
        new_artist = request.form.get('artist', '')
        new_album_title = request.form.get('album', '')

        if not song_id:
            flash('No song selected.', 'danger')
            return redirect(url_for('update_song'))

        # Handle album. Assisted with ChatGpt for syntax.
        album_id = None
        if new_album_title:
            cursor.execute("SELECT album_id FROM albums WHERE title = %s", (new_album_title,))
            album_result = cursor.fetchone()
            if album_result:
                album_id = album_result['album_id']
            else:
                cursor.execute("INSERT INTO albums (title) VALUES (%s)", (new_album_title,))
                db.commit()
                album_id = cursor.lastrowid

        # Update query was helped with chatgpt 
        fields = []
        values = []
        if new_title: 
            fields.append("title = %s")
            values.append(new_title)
        if new_artist:
            fields.append("artist = %s")
            values.append(new_artist)
        if album_id:
            fields.append("album_id = %s")
            values.append(album_id)
        if fields:
            values.append(song_id)
            sql = f"UPDATE songs SET {', '.join(fields)} WHERE song_id = %s"
            cursor.execute(sql, tuple(values))
            db.commit()
            flash('Song updated successfully!', 'success')
        else:
            flash('No changes submitted.', 'warning')

        return redirect(url_for('display_songs'))

    # GET request: show form with song options
    cursor.execute("SELECT song_id, title FROM songs ORDER BY title")
    songs = cursor.fetchall()
    return render_template('update_song.html', songs=songs)

#Display songs
@app.route('/display-songs')
def display_songs():
    query = """
    SELECT 
        s.song_id, 
        s.title AS song,  
        s.artist, 
        a.title AS album
    FROM songs s
    LEFT JOIN albums a ON s.album_id = a.album_id
    ORDER BY s.artist, a.title, s.title;
    """
    cursor.execute(query)
    songs_list = cursor.fetchall()

    #Adds view counts for DynamoDb. Syntax was helped with ChatGpt
    for song in songs_list:
        song_id_str = str(song['song_id'])  # ensure it's a string.
        try:
            response = dynamo_table.get_item(Key={'song_id': song_id_str})
            song['views'] = response.get('Item', {}).get('views', 0)
        except Exception as e:
            # fallback in case of any error
            song['views'] = 0

    return render_template('display_songs.html', songs=songs_list)

# View Count in DynamoDB
@app.route('/view-song', methods=['POST'])
def view_song():
    song_id = request.form.get('song_id')
    if not song_id:
        flash('No song selected.', 'danger')
        return redirect(url_for('display_songs'))

    try:
        # Assisted with ChatGpt to safely update view count
        dynamo_table.update_item(
            Key={'song_id': str(song_id)},
            UpdateExpression="SET #v = if_not_exists(#v, :start) + :inc",
            ExpressionAttributeNames={'#v': 'views'},
            ExpressionAttributeValues={':inc': 1, ':start': 0}
        )
        flash('Song view count updated!', 'success')
    except Exception as e:
        flash(f'Error updating views: {e}', 'danger')

    return redirect(url_for('display_songs'))

# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
