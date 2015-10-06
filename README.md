# news-aggregator
Aggregates new news articles from RSS feeds into an SQLite database.
To be used with an article clustering program to gauge topic relatedness.

The RSS feeds used are listed in feeds.txt.
To update the database with the most recent articles from these feeds, run:

```
python3 rss_parser.py
```

Use the "-c" flag to get a count of the total number of articles. The "-p" flag gets a list of the unique publisher domain names used.
