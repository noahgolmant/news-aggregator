import feedparser
import re
from datetime import datetime
from time import mktime
from db_manager import *
from article import *
import argparse


def read_rss_urls(filename):
    """ Parse filename for a list of RSS feed URLS """
    return [line for line in open(filename, 'r')]

def update_feed(url):
    feed = feedparser.parse(url)
    if feed.bozo == 1:
        print("Malformed RSS Feed")
        return
    for item in feed.entries:
        a = Article.from_feedparser(item)
        if a:
            add_entry(a)
            print('Added %s ...' % a.link)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RSS Parser Program')
    parser.add_argument("-c", "--count", action="store_true",  help='get number of articles stored')
    parser.add_argument("-p", "--publishers", action="store_true", help="list unique publishers for articles in the database")

    args = parser.parse_args()

    if args.count:
        print("Number of articles stored: %s" % num_articles())
    elif args.publishers:
        print("Article publishers in database:")
        for p in get_unique_publishers():
            print("    - %s" % p)
    else:
        for url in read_rss_urls('feeds.txt'):
            update_feed(url)

