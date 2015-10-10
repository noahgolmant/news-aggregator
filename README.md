# news-aggregator
Aggregates new news articles from RSS feeds into an SQLite database.
Clusters articles based on tf-idf vectorization and measures relatedness.

To generate a matrix representation of vectorized document data, run:

```
python3 article_processor.py
```

The RSS feeds used are listed in feeds.txt.
To update the database with the most recent articles from these feeds, run:

```
python3 rss_parser.py
```

Use the "-c" flag to get a count of the total number of articles. The "-p" flag gets a list of the unique publisher domain names used.

# To-Do
- Pipeline document processing routine to asynchronously RSS poll, filter article text, and vectorize documents
- Apply PCA dimension reduction to get 2D/3D visualization of article relatedness and clustering
