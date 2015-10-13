import psycopg2
from urllib.parse import urlparse
from contextlib import contextmanager
from article import *
import atexit

db_conn = psycopg2.connect("dbname=article_db user=postgres")

@atexit.register
def close_db():
    db_conn.close()

def perform_query(query, args=None):
    """Submit a query with any necessary args for a single result"""
    ret = (-1,)
    with db_conn.cursor() as curr:
        if args:
            curr.execute(query, args)    
        else:
            curr.execute(query)
        try:
            ret = curr.fetchone()
        except psycopg2.ProgrammingError: # No result produced
            ret = (curr.rowcount,)
        db_conn.commit()
        curr.close()
    return ret

def memoize(f):
    memo = {}
    def helper(x):
        if not x in memo:
            memo[x] = f(x)
        return memo[x]
    return helper

@memoize
def get_article_id(article):
    """ Gets the table article_id given an article object.
        Uses in-memory dict for multiple requests to the same article."""
    query = "SELECT article_id FROM articles WHERE link = %s;"
    return perform_query(query, (article.link,))[0]

def is_in_table(table, article):
    """ Checks if an article object is in the given table """
    article_id = get_article_id(article)
    if article_id < 1:
        return False
    query = "SELECT count(1) FROM {} WHERE article_id = %s;".format(table)
    return perform_query(query, (article_id,))[0]

######################
##  ARTICLES TABLE  ##
######################

def num_articles():
    """Get number of articles in the database"""
    query = "SELECT COUNT(*) FROM articles;"
    return perform_query(query)[0]

def get_url_domain(url):
    """Parse the URL domain of a specified link"""
    parsed = urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed)

def get_unique_publishers():
    """Get the set of domain names for all articles in the DB"""
    query = "SELECT link FROM articles"
    links = []
    with db_conn.cursor() as curr:
        curr.execute(query)
        links = [ get_url_domain(record[0]) for record in curr ]
        db_conn.commit()
        curr.close()
    return set(links)

def gen_articles():
    """Create a generator to yield articles from the db"""
    query = "SELECT * FROM articles;"
    with db_conn.cursor() as curr:
        curr.execute(query)
        for record in curr:
            a = Article.from_sqlentry(record)
            if is_filtered(a):
                a.filtered_text = get_filtered_text(a)
            yield a
        db_conn.commit()
        curr.close()    

def get_articles():
    """Helper to get all articles currently stored in the db"""
    return [a for a in gen_articles()]

def add_article(article):
    """ Adds an article entry with the table data:

    title (TEXT): article title
    description (TEXT): article RSS description
    link (TEXT): URL to article
    published (DATE): publication date of article
    """
    if not get_article_id(article):
        return 0
    query = "UPSERT INTO (null, title, description, link, published);"
    args = (article.title, article.description, article.link, article.published)
    return perform_query(query, args)[0]

###################
##  FAILED TABLE ##
###################

def add_to_failed(article):
    """ Adds an article to the failed table if we can't parse it"""
    query  = "INSERT INTO failed_articles(article_id, fail_date) VALUES (%s, %s);"
    id = get_article_id(article)
    if has_failed(article) or id < 1:
        return -1
    args = (id, article.published)
    return perform_query(query, args)[0]

def has_failed(article):
    """ Checks if an article has already failed parsing """
    return is_in_table('failed_articles', article)

####################
## FILTERED TABLE ##
####################

def add_to_filtered(article):
    """ Adds an article to the filtered table if successfully parsed """
    query = "INSERT INTO filtered_articles(article_id, filtered_text) VALUES (%s, %s);"
    id = get_article_id(article)
    if id < 1 or is_filtered(article):
        return -1
    args = (id, article.filtered_text)
    return perform_query(query, args)[0]

def get_filtered_text(article):
    """ Gets filtered text if an article has already been processed """
    if not is_filtered(article):
        return -1
    query = "SELECT filtered_text FROM filtered_articles WHERE article_id = %s;"
    id = get_article_id(article)
    if id < 1:
        return -1
    return perform_query(query, (id,))

def is_filtered(article):
    """ Checks if an article has already been successfully filtered """
    return is_in_table('filtered_articles', article)

##################################
## TF-CALCULATED ARTICLES TABLE ##
#################################

def add_tfs(article, term_frequencies):
    """ Stores term frequencies for an individual article """
    query = "INSERT INTO term_frequencies(article_id, term_frequencies) VALUES (%s, %s);"
    id = get_article_id(article)
    if id < 1 or has_tfs(article):
        return -1
    args = (id, term_frequences)
    return perform_query(query, args)[0]

def get_tfs(article):
    """ Gets the term frequencies for a processed article """
    query = "SELECT term_frequencies FROM term_frequencies WHERE ( article_id = %s );"
    if not has_tfs(article):
        return None
    id = get_article_id(article)
    if id < 1:
        return None
    return perform_query(query, (id,))[0]

def has_tfs(article):
    return is_in_table('term_frequencies', article)

################################
## IDF-CALCULATED TERMS TABLE ##
################################

def add_idf(term, idf):
    if has_idf(term):
        return 0
    query = "INTO inverse_document_frequencies(term, idf) VALUES (%s, %s);"
    args = (term, idf)
    return perform_query(query, args)[0]

@memoize
def get_idf(term):
    query = "SELECT idf FROM inverse_document_frequencies WHERE term = %s;"
    return perform_query(query, (term,))[0]

def has_idf(term):
    return is_in_table('inverse_document_frequencies', term)

def get_idfs():
    query = "SELECT idf FROM inverse_document_frequencies;"
    return perform_query(query)
