from math import log10

def max_frequency(document):
    """Calculated largest term frequency of terms in a document"""
    max_f = 1
    for w in set(document):
        max_f = max(max_f, term_frequency(w, document))
    return max_f

def augmented_term_frequency(term, document, max_frequency=1):
    """Calculate augmented term frequency of a term in a document
    
    tf(t,d) = 0.5 + (0.5 * f(t,d))
                    --------------
                    max{ f(t,d) : t in d }

    where f(t,d) is the number of times t occurs in document d.
    """
    return 0.5 + (0.5 * document.count(term)) / max_raw_frequency


def inv_document_frequency(term, document_list):
    """Logarithmically sclaed fraction of documents that contain the term"""
    num_docs_with_t = len([d for d in document_list if term in d])
    num_docs = len(document_list)
    return log10(num_docs / (1 + num_docs_with_t))

def tf_idf(term, document, document_list):
    """Calculated term-frequency * inverse document frequency to represent 
       significance of a term in context of the document and the corpus as a whole"""
    return augmented_term_frequency(term, document) * inv_document_frequency(term, document_list)

def unique_terms(document_list):
    """Total set of unique terms in a corpus."""
    term_set = set()
    for d in document_list:
        term_set += d
    return list(term_set)

def vectorize_document(document, document_list, unique_terms):
    """Returns a normalized vector representation of the document in the corpus space"""
    vec = [tf_idf(t, document, document_list) for t in unique_terms]
    vec_len = sqrt(sum([t*t for t in vec]))
    return [t / vec_len for t in vec)
