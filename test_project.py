import pytest
import os

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker

from lyricsgenius import Genius
from dotenv import load_dotenv

from unittest import mock
from unittest.mock import patch
from requests import HTTPError

from models import Song
from project import word_length_frequency, get_songs_from_database, get_song_from_genius, avg_word_length_by_year

load_dotenv()
token = os.getenv("TOKEN")

# These are for confguring the SQLAlchemy
engine = create_engine("sqlite+pysqlite:///songs.db", echo=False, future=True)
Session = sessionmaker(engine)
session = Session()


def test_word_length_frequency():
    word_list = ["aaa", "", "bbb", "music", "physics"]
    frequency = {0: 20.0, 1: 0, 2: 0, 3: 40.0, 4: 0, 5: 20.0, 6: 0, 7: 20.0}
    assert word_length_frequency(word_list) == frequency


def test_get_songs_from_database():
    test_song = Song(title="test_song", artist="test_artist")
    session.add(test_song)
    session.commit()
    assert get_songs_from_database(title="test_song", artist="test_artist").first().title == "test_song"
    assert get_songs_from_database(title="test_song").first().artist == "test_artist"
    session.delete(test_song)
    session.commit()
    assert get_songs_from_database(title="test_song").first() == None
    session.close()


def test_avg_word_length_by_year():
    assert isinstance(avg_word_length_by_year(), dict)


def test_get_songs_from_database_no_title():
    with pytest.raises(ValueError):
        get_songs_from_database(title="", artist="test_artist")


def test_get_song_from_genius():
    assert get_song_from_genius(title="zombie", artist="cranberries").first().released == 1994


def test_genius_API():
    genius = Genius(token)
    song = genius.search_song(title="Waterloo", artist="ABBA")
    assert song.title == 'Waterloo'
    assert song.artist == 'ABBA'
    assert song.lyrics.startswith("Waterloo Lyrics[Verse 1]\nMy, my - at Waterloo, Napoleon did surrender")


def test_word_list():
    lyrics = "test song lyrics\n[this shouldn't appear]    One  two 4, [remove] &*$#@!)( finally wit's end78Embed"
    song = Song(title="test", artist="test", lyrics=lyrics)
    assert song.word_list() == ["One", "two", "finally", "wits", "end"]


def test_num_words():
    lyrics = "one two three four five six seven"
    song = Song(title="test", artist="test", lyrics=lyrics)
    assert song.num_words() == 7


def test_num_distinct_words():
    lyrics = "four one two three four five six four seven four seven physics pizza"
    song = Song(title="test", artist="test", lyrics=lyrics)
    assert song.num_distinct_words() == 9
