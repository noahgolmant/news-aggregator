from db_manager import get_articles, num_articles
from text_processor import *
import numpy
import time
import sys

# t x n matrix representing entire vectorized document corpus

def generate_doc_matrix():
    documents = []

    num = num_articles()

    i = 0
    for article_block in get_articles():
        for a in article_block:
            text = a.filter_article_text()
            documents.append(text)
            i += 1
            sys.stdout.write("\rArticles filtered: %f%%" % ((i / num) * 100))
            sys.stdout.flush()
    
    print('Getting set of unique terms in documents ...')
    unique_set = unique_terms(documents)
    print('Vectorizing and normalizing documents ...')
    vectorized_docs = [vectorize_document(d, documents, unique_set) for d in documents]
    return numpy.column_stack(vectorized_docs)

def print_doc_matrix_info():
    document_matrix = generate_doc_matrix()
    if not document_matrix:
        print('Document matrix is null!')
        return
    print("Doc matrix shape: %s" % document_matrix.shape)
    #print("Doc matrix:")
    #print(document_matrix)

if __name__ == '__main__':
    print_doc_matrix_info()
