from db_manager import *
from text_processor import *
from multiprocessing import Process
import numpy
import time
import sys
import shelve
import signal

def print_progress(msg, i, max_val, line_num=0, show_frac=True):
    """Print progress of some process"""
    prcnt = (i / max_val) * 100
    if show_frac:
        sys.stdout.write("\n"*line_num + "\r{0}: {1:.2f}%    ({2}/{3})".format(msg, prcnt, i, max_val))
    else:
        sys.stdout.write("\r{0}: {1:.2f}%".format(msg, prcnt))
    sys.stdout.flush()

def process_articles(articles):
    """Process all articles and store filtered article text"""
    num = num_articles()
    i = 0
    print('Downloading and parsing articles...')
    for a in articles:
        i += 1
        # Pass if the article has already been processed
        if has_failed(a):
            continue
        if is_filtered(a):
            a.filtered_text = get_filtered_text(a)
            continue
        elif not a.filtered_text:
            print("process_articles(): Failed to filter article: " + a.link)
            add_to_failed(a)
            continue
        add_to_filtered(a)
        print_progress("Articles filtered", i, num)
    return [a for a in articles if a.filtered_text is not None]

def process_idfs(articles, doc_lst=None):
    """Process inverse document frequencies for a corpus and its unique terms."""
    if not doc_lst:
        doc_lst = [a.filtered_text for a in articles]
    term_lst = unique_terms(doc_lst)
    i = 0
    num = len(term_lst)
    for t in term_lst:
        print_progress('IDFs', i, num)
        i += 1
        idf = inv_document_frequency(t, doc_lst)
        add_idf(t, idf)

def process_tfs(articles, doc_lst=None):
    """Process term frequencies for each document in the corpus"""
    if not doc_lst:
        doc_lst = [a.filtered_text for a in articles]
    term_lst = unique_terms(doc_lst)
    for a in articles:
        text = a.filtered_text
        max_f = max_frequency(text)
        doc_tfs = []
        for t in term_lst:
            tf = augmented_term_frequency(t, text, max_f)
            doc_tfs.append(tf)
        add_tfs(a, doc_tfs)

def vectorize_articles(articles):
    vectorized = []
    for a in articles:
        term_frequencies = get_tfs(a)
        vectorized_a = term_frequencies[:]
        if not term_frequencies:
            continue
        inv_doc_frequencies = get_idfs()
        assert len(term_frequencies) == len(inv_doc_frequencies), "Article should reference all possible terms"
        for i in range(len(vectorized_a)):
            vectorized_a[i] *= inv_doc_frequencies[i]
        vectorized.append(vectorized_a)
    return vectorized

def generate_doc_matrix():
    """Generate a document matrix as a concatenation of the vectorized documents"""
    articles = get_articles()
    articles = process_articles(articles)

    doc_lst = [a.filtered_text for a in articles]
    # Calculate corpus inverse document frequencies in parallel with each document's term frequency calculation
    print('\nProcessing article term frequencies and inverse doc frequencies ...')
    idf_process = Process(target=process_idfs, args=(articles,doc_lst[:]))
    tf_process  = Process(target=process_tfs, args=(articles,doc_lst[:]))

    idf_process.start()
    tf_process.start()
    idf_process.join()
    tf_process.join()
    print('Vectorizing articles ...')
    vectorized = vectorize_articles(articles)    
    print('Finished vectorizing. Concatenating to matrix.')
    return numpy.column_stack([v for v in vectorized])

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
