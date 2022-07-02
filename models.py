"""
    This holds the Song model
    This should be run first with python models.py to create the
    database tables
"""
import re

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

engine = create_engine("sqlite+pysqlite:///songs.db", echo=False, future=True)
Base = declarative_base()

class Song(Base):

    """ Song Model """

    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    genius_id = Column(Integer, unique=True)
    title = Column(String)
    artist = Column(String)
    released = Column(Integer)
    lyrics = Column(String)

    def __repr__(self):
        return f"{self.title} by {self.artist} released in {self.released}"


    def word_list(self):

        """
            Remove [music descriptions], non words, etc... from the lyrics along with
            the embed code given at the end, and return a list of the words without
            any punctuation so that the character lengths can be analyzed
        """

        lyrics = self.lyrics
        if "\n" in lyrics:
            lyrics = lyrics.split("\n", 1)[1]
        lyrics = re.sub(r"\[[^\]]*\]", "", lyrics)
        lyrics = re.sub(r"\d+Embed", "", lyrics)
        lyrics = re.sub(r"\'", "", lyrics)
        lyrics = re.sub(r"\W", " ", lyrics)
        lyrics = re.sub(r"\d", "", lyrics)
        lyrics = re.sub(r" {2,}", " ", lyrics)
        lyrics = lyrics.strip()
        return lyrics.split(" ")


    def num_words(self):

        """ Count the total number of words in the lyrics """

        words = self.word_list()

        return len(words)


    def num_distinct_words(self):

        """ Count the number of unique words thesong has """

        words = self.word_list()
        word_set = {word for word in words}

        return len(word_set)


    def avg_word_length(self):

        """ Find the average word length """

        average = 0
        words = self.word_list()

        for word in words:
            average += len(word)

        return round((average / self.num_words()), 2)


Base.metadata.create_all(engine)
