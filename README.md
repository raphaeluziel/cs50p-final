# Song Lyric Analyzer
#### Video Demo:  https://youtu.be/JC8po5UzfJg
#### Description:

The main objective of my project is to do a word length (number of characters in the words) analysis of song lyrics.  It's based on the [Genius API](https://docs.genius.com/), which provides the lyrics for a song given it's title.  Once a song is found, an analysis is run on the song including:

1. The total number of words in the lyrics
2. The number of distinct words in the lyrics
3. The average word length of all the words in the lyrics

Then, using [Matplotlib](https://matplotlib.org/), a graph is drawn with word lengths in the x-axis, and the percentage of words of that word length compared to all the words in the lyrics.

The purpose of the database is to store information on all the songs downloaded from Genius, so that further analysis can be done on *all* the songs, or perhaps a subset of them in the future.  For now, I chose to analyze word length by year released, again graphing the results.  The average word length versus year is graphed in hopes of determining if there is a trend.  Thus far, my sample size is too small to come to any conclusion, but as more songs are added, who knows?  I am using [SQLAlchemy](https://www.sqlalchemy.org/) ORM to query the database.

In addition to the required files I have the following two files:

**models.py**  
Taking my experience with Django, I store the `Song` class, which will store the song's title, artist, year released, and the actual lyrics as well.  The class has several methods, including `num_words`, `num_distinct_words`, and `average_word_length`, and finally the `word_list` method, which uses the `re` module to remove all non letters from the lyrics, so the analysis of word length can be done.

**songs.db**  
This is the SQLite database that stores all the data I have downloaded.  I'm hoping to include it so that the user does not have to start from scratch downloading songs from the Genius API.

#### Running the Program

🔴🔴🔴  **IMPORTANT!**  🔴🔴🔴  
In order to run this program you will need to register for a FREE [Client Access Token](https://genius.com/api-clients) from [Genius](https://docs.genius.com/).  The token should be placed in a file called '.env' in the same directory as all other files.  Otherwise, the program, while it will work with any songs already in the database, will not authorize you to fetch any other songs from Genius.

**.env**

    TOKEN=[enter your token here]

This way the following lines in **project.py** will work as intended:  

    # These are needed for the Genius API
    token = os.getenv("TOKEN")
    genius = Genius(token)

---
**Now to actually run the program**  
There are two methods.  First is to just run `python project.py`, which will ask for a title to a song (required), and the artist name (not required, but helps if there are multiple artists with the same song name).  The other method is to pass in the title and/or artist using command line arguments, as in:

    python project.py --title waterloo --artist abba  

Again the `--artist` or `-a` argument is optional.  

If a song title that is already in the database (such as "*Waterloo*") is given, the song will be immediately retrieved.  If there are multiple songs with the same title (such as, in my database, "*Xanadu*", which is a title for songs by *Rush* as well as *Olivia Newton John*), then each is retrieved, and analyzed one a time.

The analysis section first pops open a graph of the particular song, assuming that their is a program that Matplotlib can use to show the graph, as well as the other stats of the song, which will be given in the console.  When the graph is closed, the next song (if multiple songs are returned in the query) will be analyzed.  When the final graph is closed, *another* graph will automatically pop open with the frequency analysis of **all** the songs currently in the database (there are currently approximately 50 songs as of this writing).
