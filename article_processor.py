from db_manager import get_articles, num_articles
from text_processor import *
import numpy
import time
import sys
import shelve
import signal

sys.stdout.write('Opening doc_vectors shelf...')
doc_vec_filename = 'doc_vectors.dat'
doc_vectors = shelve.open(doc_vec_filename)
sys.stdout.write(' done.\n')
sys.stdout.flush()

def ctrl_c_handler(signum, frame):
    print('\n\nSyncing persistent document vector storage')
    try:
        doc_vectors.close()
    except:
        sys.exit(0)
    sys.exit(0)

def store_filtered_document(doc):
    try:
        doc_vectors[doc.link] = doc.filtered_text
    except ValueError:
        print('Tried to store doc in closed shelf')
        sys.exit(0)
        
def is_doc_stored(doc):
    try:
        return doc.link in doc_vectors.keys()
    except:
        print('Tried to check value in closed shelf')
        sys.exit(0)
        return True

# t x n matrix representing entire vectorized document corpus
def generate_doc_matrix():
    documents = []
    num = num_articles()
    i = 0
    for article_block in get_articles():
        for a in article_block:
            i += 1
            if is_doc_stored(a):
                continue

            a.filter_article_text()
            if not a.filtered_text:
                print('generate_doc_matrix(): Failed to store article: ' + a.link)
                continue

            store_filtered_document(a)
            documents.append(a.filtered_text)

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
    signal.signal(signal.SIGINT, ctrl_c_handler) 
    print_doc_matrix_info()
