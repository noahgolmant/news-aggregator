import sqlite3
from urllib.parse import urlparse
from contextlib import contextmanager
from article import *

articles_db = sqlite3.connect('articles.db')
cursor = articles_db.cursor()
table_name = 'articles'

article_rows = [ 'title', 'description', 'link', 'published' ]    

def query(sql, args=None):
    """Executes an SQLite query on the article database"""
    if args:
        cursor.execute(sql,args)
    else:
        cursor.execute(sql)
    articles_db.commit()
    return cursor.fetchall()

def query_gen(sql, args=None, block_size=20):
    """Creates a generator for a specific query that
       yields BLOCK_SIZE database entries per iteration.
    """
    def query_gen_helper():
        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)
        articles_db.commit()
        while True:
            results = cursor.fetchmany(block_size)
            if not results:
                break
            yield results
    return query_gen_helper

def num_articles():
    """Get the number of articles in the database"""
    sql = "SELECT COUNT(*) FROM {}".format(table_name)
    ret = query(sql)
    return ret[0][0]

def get_url_domain(url):
    """Parse the URL domain of a specified link"""
    parsed = urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed)

def get_unique_publishers():
    """Get the set of domain names for all articles in the DB"""
    sql = "SELECT link FROM {}".format(table_name)
    ret = query(sql)
    links = [get_url_domain(r[0]) for r in ret]
    return set(links)

def get_articles(block_size=20):
    """Iterate over blocks of BLOCK_SIZE articles from the database"""
    sql = "SELECT * FROM {}".format(table_name)
    article_gen = query_gen(sql,block_size=20)
    for article_block in article_gen():
        #a = Article.from_sqlentry(article_block[0])
        yield [Article.from_sqlentry(a) for a in article_block]

def add_entry(article):
    """ Adds an article entry with the table data:

    title (TEXT): article title
    description (TEXT): article RSS description
    link (TEXT): URL to article
    published (DATE): publication date of article
    """
    sql = "INSERT OR IGNORE INTO {0} VALUES (null, ?, ?, ?, ?)".format(table_name)
    return query(sql, args=article.sql_entry())
