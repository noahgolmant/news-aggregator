from db_manager import get_articles, num_articles
from text_processor import *
import numpy
import time
import sys
import shelve
import signal

sys.stdout.write('Opening flat file data...')
filtered_text_shelf = shelve.open('filtered_text.dat')
failed_docs_shelf = shelve.open('failed_docs.dat')
vectorized_docs_shelf = shelve.open('vectorized_docs.dat')
sys.stdout.write(' done.\n')
sys.stdout.flush()

def close_shelves():
    print('\n\nSyncing persisent document vector storage')
    try:
        filtered_text_shelf.close()
        failed_docs_shelf.close()
        vectorized_docs_shelf.close()    
    except:
        sys.exit(0)
    sys.exit(0)

def ctrl_c_handler(signum, frame):
    """Make sure to sync flat file storage on exit"""
    close_shelves()

def store_to_shelf(key, val, shelf):
    try:
        shelf[key] = val
    except ValueError:
        print('Tried to store doc in closed shelf')
        sys.exit(0)
        
def is_key_stored(key, shelf):
    try:
        return key in shelf.keys()
    except:
        print('Tried to check value in closed shelf')
        sys.exit(0)
        return True

def print_progress(msg, i, max_val, show_frac=True):
    """Print progress of some process"""
    prcnt = (i / max_val) * 100
    if show_frac:
        sys.stdout.write("\r{0}: {1:.2f}%    ({2}/{3})".format(msg, prcnt, i, max_val))
    else:
        sys.stdout.write("\r{0}: {1:.2f}%".format(msg, prcnt))
    sys.stdout.flush()

def process_articles(doc_shelf, failed_shelf):
    """Process all articles and store filtered article text to a shelf"""
    num = num_articles()
    i = 0
    print('Downloading and parsing articles...')
    for article_block in get_articles():
        for a in article_block:
            i += 1
            # Pass if the article has already been processed
            if is_key_stored(a.link, doc_shelf) or is_key_stored(a.link, failed_shelf):
                continue
            a.filter_article_text()
            if not a.filtered_text:
                print("process_articles(): Failed to filter article: " + a.link)
                failed_shelf[a.link] = 1
                continue

            store_to_shelf(a.link, a.filtered_text, doc_shelf)
            print_progress("Articles filtered", i, num)

def vectorize_articles(filtered_shelf, vec_shelf):
    """Create a vector representation of the filtered articles using tf-idf"""
    document_lst = list(filtered_shelf.values())
    unique_set = unique_terms(document_lst)
    print('Vectorizing articles...')
    i = 0
    num = len(document_lst)
    for link, doc in filtered_shelf.items():
        print_progress("Vectorized articles", i, num)
        if link in vec_shelf.keys():
            v = vec_shelf[link]
        else:
            v = vectorize_document(doc, document_lst, unique_set)
            store_to_shelf(link, v, vec_shelf)
        i += 1        

def generate_doc_matrix():
    """Generate a document matrix as a concatenation of the vectorized document columns"""
    process_articles(filtered_text_shelf, failed_docs_shelf)
    vectorize_articles(filtered_text_shelf, vectorized_docs_shelf)
    print('Finished vectorizing. Concatenating to matrix.')
    return numpy.column_stack(vectorized_docs_shelf.values())

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
    close_shelves()
