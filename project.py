"""
    Song lyrics analyzer
    Searches for a song, then fetches it's lyrics, and finally does
    a frequency analysis of the words used in the lyrics
"""

import os
import sys
import argparse

import matplotlib.pyplot as plt

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker

from requests.exceptions import HTTPError, Timeout

from lyricsgenius import Genius
from dotenv import load_dotenv

from models import Song

load_dotenv()

# These are for confguring the SQLAlchemy
engine = create_engine("sqlite+pysqlite:///songs.db", echo=False, future=True)
Session = sessionmaker(engine)
session = Session()

# These are needed for the Genius API
token = os.getenv("TOKEN")
genius = Genius(token)


def get_args():

    """ To parse command line arguments """

    description = ("This program searches for lyrics, then analyzes the frequency of words "
                   "with different character lengths. NOTE: Title of song is required whether "
                   "using command line arguments or inputs. Adding the artist will narrow "
                   "down the search in case two songs have the same title.")

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--title", "-t", help="Song title (REQUIRED with command line arguments)")
    parser.add_argument("--artist", "-a", help="Song's artist")

    return parser.parse_args()


def get_songs_from_database(title, artist=""):

    """ Return a SQLAlchemy Query of songs matching title, artist from database. """

    if not title:
        raise ValueError("Title is required.")

    title = title.lower()
    artist = artist.lower() if artist else ""

    songs = session.query(Song).filter(func.lower(Song.title) == title)
    if artist:
        songs = songs.filter(func.lower(Song.artist) == artist)

    return songs


def get_song_from_genius(title, artist=""):

    """
        Fetch a song from the Genius API.  Then check if it's already in the databse.
        If it is not, add it to the database.  Either way, return a SQLAlchemy Query of songs.
        If not found return an EMPTY query.
    """

    if song_genius := genius.search_song(title=title, artist=artist):
        released = song_genius.to_dict()["release_date_components"]
        released = released if released else None

        if not(songs := get_songs_from_database(title=song_genius.title, artist=song_genius.artist).first()):
            song = Song(genius_id=song_genius.id,
                        title=song_genius.title,
                        artist=song_genius.artist,
                        released = released["year"] if released else None,
                        lyrics=song_genius.lyrics)
            session.add(song)
            session.commit()

        songs = session.query(Song).filter(Song.title == song_genius.title, Song.artist == song_genius.artist)

    else:
        songs = session.query(Song).filter(False)   # Song not found, return empty Query

    return songs


def word_length_frequency(word_list):

    """
        Create a dictionary where the keys are the character lengths of words,
        and the values are the percentages of the words in the lyrics with that length
    """

    total_words = len(word_list)

    # Create a dictionary with keys equal to word lengths (45 is the longest word)
    frequency = {i: 0 for i in range(45)}

    # Add words to the appropriate place in the dictionary
    for word in word_list:
        frequency[len(word)] += 100 / total_words

    # Round off the dictionary
    frequency = {i: round(frequency[i], 2) for i in range(45)}

    # Remove keys with long character lengths that do not appear
    for key in list(reversed(frequency)):
        if frequency[key] == 0:
            frequency.pop(key)
        else:
            break

    return frequency


def analyze(song):

    """ Subroutine for printing analysis and graphing the results for a particular song """

    x, y = zip(*word_length_frequency(song.word_list()).items())
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.set_ylabel("percent")
    ax.set_xlabel("word length")
    ax.set_title(f"Lyrics Analyzer for {song}")
    ax.plot(x, y, color="orange")

    print(f"\nLyrics analysis of {song}")
    print("---------------------------------------")
    print("Total number of words: ", song.num_words())
    print("Number of distinct words: ", song.num_distinct_words())
    print("Average word length: ", song.avg_word_length())

    plt.show()
    plt.close()


def avg_word_length_by_year():

    """
        Analyze the average word length of songs in database by year released.
        This will return a dictionary with year as key, and average word length as value
    """

    songs = session.query(Song).order_by(Song.released)

    total_characters_in_year = {song.released: 0 for song in songs}
    avg_word_length_by_year = {song.released: 0 for song in songs}

    for song in songs:
        total_characters_in_year[song.released] += song.num_words()
        avg_word_length_by_year[song.released] += len("".join(song.word_list()))

    for year in avg_word_length_by_year:
        avg_word_length_by_year[year] = round((avg_word_length_by_year[year] / total_characters_in_year[year]), 2)

    return avg_word_length_by_year


def graph_avg_word_len_by_year():

    """ Subroutine for printing and graphing average word length by year for all songs in database """

    x, y = zip(*avg_word_length_by_year().items())
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_ylabel('average word length')
    ax.set_xlabel('year')
    ax.set_title('Average Word Length by Year')
    ax.plot(x, y, color="red")
    plt.show()
    plt.close()


def main():

    """ This is the main function """

    args = get_args()

    title = args.title if len(sys.argv) > 1 else input("Song title: ")
    artist = args.artist if len(sys.argv) > 1 else input("Artist name: ")

    try:
        songs = get_songs_from_database(title, artist)
    except ValueError as err:
        sys.exit(err)

    if not songs.first():   # Song was not found in database
        try:
            songs = get_song_from_genius(title, artist)
        except HTTPError as err:
            print(err.errno)    # status code
            print(err.args[0])  # status code
            print(err.args[1])  # error message
        except Timeout:
            print("Genius API experienced a timeout error.  Please try your search again.")

    if songs.first():
        for song in songs:
            analyze(song)

    graph_avg_word_len_by_year()

    session.close()


if __name__ == "__main__":
    main()
