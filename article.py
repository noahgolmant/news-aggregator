from datetime import datetime
from time import mktime
import feedparser
import re

ARTICLE_ENTRY_LENGTH = 4

class ArticleFormatException(Exception):
    pass

class Article:

    def __init__(self, raw_data):
        if len(raw_data) != ARTICLE_ENTRY_LENGTH:
            raise ArticleFormatException("Wrong number of entries for article. Expected {0} but got {1}".format(ARTICLE_ENTRY_LENGTH, len(raw_data)))

        self.__title        = self.__strip_tags(raw_data[0])
        self.__description  = self.__strip_tags(raw_data[1])
        self.__link         = raw_data[2]
        self.__published    = self.__iso_formatted(raw_data[3])

    @classmethod
    def from_feedparser(cls, item):
        """ Gets an article object from a feedparser stream
        """
        try:
            return cls((item.title, item.description, item.link, item.published_parsed))
        except AttributeError:
            return None
            # TODO: crawl for URL if not available
    @property
    def title(self):
        return self.__title

    @property
    def description(self):
        return self.__description

    @property
    def link(self):
        return self.__link

    @property
    def published(self):
        return self.__published

    def sql_entry(self):
        return (self.title, self.description, self.link, self.published)

    # Strip formatting from raw RSS entry
    def __strip_tags(self, str):
        return re.sub('<[^<]+?>', '', str)
    # Get ISO-formatted date string for db entry
    def __iso_formatted(self, date):
        return datetime.fromtimestamp(mktime(date))
