from datetime import datetime
from time import mktime, strptime
import feedparser
import re
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import newspaper
import db_manager
from article import *
import argparse
import string

ARTICLE_ENTRY_LENGTH = 4
stop_words = stopwords.words('english')
stemmer = SnowballStemmer('english')

class ArticleFormatException(Exception):
    pass

class Article:

    def __init__(self, raw_data):
        if len(raw_data) != ARTICLE_ENTRY_LENGTH:
            raise ArticleFormatException("Wrong number of entries for article. Expected {0} but got {1}".format(ARTICLE_ENTRY_LENGTH, len(raw_data)))
        self.title         = self.__strip_tags(raw_data[0])
        self.description   = self.__strip_tags(raw_data[1])
        self.link          = raw_data[2]
        self.published     = raw_data[3]
        self._text          = None
        self._filtered_text = None

    @classmethod
    def from_feedparser(cls, item):
        """ Gets an article object from a feedparser stream
        """
        try:
            return cls((item.title, item.description, item.link, item.published_parsed))
        except AttributeError:
            return None
            # TODO: crawl for URL if not available

    @classmethod
    def from_sqlentry(cls, entry):
        """Gets article object from an SQL row entry"""
        #published = strptime(entry[-1], '%Y-%m-%d %H:%M:%S')
        
        return cls((entry[1],entry[2],entry[3],entry[-1]))

    def sql_entry(self):
        return (self.title, self.description, self.link, self.published)

    # Strip formatting from raw RSS entry
    def __strip_tags(self, str):
        return re.sub('<[^<]+?>', '', str)
    # Get ISO-formatted date string for db entry
    def __iso_formatted(self, date):
        return datetime.fromtimestamp(mktime(date))
    
    @property
    def text(self):
        """Uses newspaper module to get main body of an article"""
        if self._text:
            return self._text
        try:
            news_article = newspaper.Article(self.link)
            news_article.download()
            news_article.parse()
        except:
            print('Failed to download article: ' + self.link)
            return None
        # filter out punctuation
        text = ''.join([c for c in news_article.text if c not in string.punctuation])
        self._text = [w.lower() for w in text.split()]
        return self._text

    @property
    def filtered_text(self):
        """Filters out stop words and stems each word to get usable text tokens"""
        if self._filtered_text:
            return self._filtered_text
        elif db_manager.is_filtered(self):
            self._filtered_text = db_manager.get_filtered_text(self)
            return self._filtered_text
        elif db_manager.has_failed(self):
            return None
        elif not self.text:
            print('No article text from get_article_text()')
            return None

        self._filtered_text = [stemmer.stem(w) for w in self.text if w not in stop_words]
        return self._filtered_text

    @filtered_text.setter
    def filtered_text(self, text):
        self._filtered_text = text


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Article function tester')
    parser.add_argument("-f", "--filter", action="store_true", help="Test text filter on a sample article")
    parser.add_argument("-p", "--parse", action="store_true", help="Test text parser on a sample article")

    args = parser.parse_args()

    query = "SELECT * FROM articles LIMIT 1;"
    ret = db_manager.query(query)
    test_article = Article.from_sqlentry(ret[0])
    if args.filter:
        print(test_article.filter_article_text())
    elif args.parse:
        print(test_article.get_article_text())
