# Project One Song Library

**CS178: Cloud and Database Systems — Project #1**
**Author:** [Robert Schleicher]
**GitHub:** [RobertSchleicher]

---

## Overview

This project uses flask app to have a website that tracks songs,artists, and artists. Users can add, update, delete, view songs.
It has a relational database for structure of song and album data and uses non-relational dynamodb to use to track songs views. Users can hit view song button to add view to song
---

## Technologies Used

- **Flask** — Python web framework
- **AWS EC2** — hosts the running Flask application
- **AWS RDS (MySQL)** — relational database for [songs, albums, and artists]
- **AWS DynamoDB** — non-relational database for [stores view counts for each song]
- **GitHub Actions** — auto-deploys code from GitHub to EC2 on push

---

## Project Structure

```
ProjectOne/
├── flaskapp.py          # Main Flask application — routes and app logic
├── dbCode.py            # Database helper functions (MySQL connection + queries)
├── templates/
│   ├── home.html        # Landing page
│   ├── add_song.html    # Form to add new song
│   ├── delete_song.html   # Form to delete new song
│   ├── update_song.html   # Form to update song
│   ├── display_songs.html #Displays list of song with views
│   
├── .gitignore       #Excludes cred.py and other sensitive files
├── creds.py          # credentials file
└── README.md
```

---

## How to Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Install dependencies:

   ```bash
   pip3 install flask pymysql boto3
   ```

3. Set up your credentials (see Credential Setup below)

4. Run the app:

   ```bash
   python3 flaskapp.py
   ```

5. Open your browser and go to `http://127.0.0.1:8080`

---

## How to Access in the Cloud

The app is deployed on an AWS EC2 instance. To view the live version:

```
http://[your-ec2-public-ip]:8080
```

_(Note: the EC2 instance may not be running after project submission.)_

---

## Credential Setup

This project requires a `creds.py` file that is **not included in this repository** for security reasons.

Create a file called `creds.py` in the project root with the following format (see `creds_sample.py` for reference):

```python
# creds.py — do not commit this file
host = "your-rds-endpoint"
user = "admin"
password = "your-password"
db = "your-database-name"
aws_access_key = "your-aws-access-key"
aws_secret_key = "your-aws-secret-key"
```

---

## Database Design

### SQL (MySQL on RDS)

<!-- Briefly describe your relational database schema. What tables do you have? What are the key relationships? -->

**Example:**

- `[albums]` — stores [album titles]; primary key is `[album_id]`
- `[songs]` — stores [song title, artist, and album_id]; Primary key is song_id and foreign key album_id links to `[albums]`

The JOIN query used in this project: I got song details along with their album names by using album_id with a left join
### DynamoDB
- **Table name:** `[song_stats]`
- **Partition key:** `[song_id]`
- **Used for:** [ I used this to track the number of views for each song. Each song has a song_id and views (number) when the user clicks the "view song", the app increase the view count.]

---

## CRUD Operations

| Operation | Route              | Description                                   |
| --------- | -------------------| ----------------------------------------------|
| Create    | `/[add-song]`      | [Adds new song to MySQL database]             |
| Read      | `/[display-songs]` | [Displays all songs with song info and views] |
| Update    | `/[update-song]`   | [Update song info(title,artist, and album)]   |
| Delete    | `/[delete-song]`   | [Delete a song from MySQL database]           |

---

## Challenges and Insights
I had a decent amount of work was ensuring all my CRUD operations worked safely. I kept getting issues with my display. I liked using the different flash messages and colored buttons to improve overall feel of website. It was also pretty tough deciding how to integrate both MySQL and DynamoDB. It helped distigush the different needs between structured and unstructured data. 
---

## AI Assistance

I used ChatGPT to help with HTML files, Flask routes syntax/structure, and to overall troubleshoot error messages.