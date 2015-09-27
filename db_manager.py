import sqlite3
from urllib.parse import urlparse
from contextlib import contextmanager

articles_db = sqlite3.connect('articles.db')
cursor = articles_db.cursor()
table_name = 'articles'

article_rows = [ 'title', 'description', 'link', 'published' ]    

def query(sql, args=None):
    if args:
        cursor.execute(sql,args)
    else:
        cursor.execute(sql)
    articles_db.commit()
    return cursor.fetchall()

def num_articles():
    sql = "SELECT COUNT(*) FROM {}".format(table_name)
    ret = query(sql)
    return ret[0][0]

def get_url_domain(url):
    parsed = urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed)

def get_unique_publishers():
    sql = "SELECT link FROM {}".format(table_name)
    ret = query(sql)
    links = [get_url_domain(r[0]) for r in ret]
    return set(links)

def add_entry(article):
    """ Adds an article entry with the table data:

    title (TEXT): article title
    description (TEXT): article RSS description
    link (TEXT): URL to article
    published (DATE): publication date of article
    """
    sql = "INSERT OR IGNORE INTO {0} VALUES (null, ?, ?, ?, ?)".format(table_name)
    return query(sql, args=article.sql_entry())
