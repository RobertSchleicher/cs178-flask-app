CREATE DATABASE IF NOT EXISTS music_db;
USE music_db;
-- Artists table
CREATE TABLE artists (
    artist_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    genre VARCHAR(50),
    country VARCHAR(50)
);

-- Albums table
CREATE TABLE albums (
    album_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    release_year YEAR,
    label VARCHAR(50)
);

-- Songs table
CREATE TABLE songs (
    song_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    duration TIME,
    album_id INT,
    FOREIGN KEY (album_id) REFERENCES albums(album_id)
);

-- Join table for many-to-many relationship between songs and artists
CREATE TABLE song_artists (
    song_id INT,
    artist_id INT,
    PRIMARY KEY (song_id, artist_id),
    FOREIGN KEY (song_id) REFERENCES songs(song_id),
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
);

## Sample data insertion
INSERT INTO artists (name, genre, country) VALUES
('Taylor Swift', 'Pop', 'USA'),
('Ed Sheeran', 'Pop', 'UK'),
('Beyoncé', 'R&B', 'USA'),
('Drake', 'Hip-Hop', 'Canada'),
('Adele', 'Pop', 'UK');

INSERT INTO albums (title, release_year, label) VALUES
('1989', 2014, 'Big Machine Records'),
('Divide', 2017, 'Asylum Records'),
('Lemonade', 2016, 'Parkwood Entertainment'),
('Scorpion', 2018, 'Young Money Entertainment'),
('25', 2015, 'XL Recordings');

InSERT INTO songs (title, duration, album_id) VALUES
('Blank Space', '00:03:51', 1),
('Shape of You', '00:03:53', 2),
('Formation', '00:03:26', 3),
("God's Plan", '00:03:18', 4),
('Hello', '00:04:55', 5);

INSERT INTO song_artists (song_id, artist_id) VALUES
(1, 1), -- Blank Space by Taylor Swift
(2, 2), -- Shape of You by Ed Sheeran
(3, 3), -- Formation by Beyoncé
(4, 4), -- God's Plan by Drake
(5, 5); -- Hello by Adele