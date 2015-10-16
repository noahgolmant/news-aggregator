from math import log10, sqrt
from random import randint
import sys
from functools import reduce
from operator import or_

def max_frequency(document):
    """Calculated largest term frequency of terms in a document"""
    max_f = 1
    for w in set(document):
        max_f = max(max_f, augmented_term_frequency(w, document))
    return max_f

def augmented_term_frequency(term, document, max_frequency=1):
    """Calculate augmented term frequency of a term in a document
    
    tf(t,d) = 0.5 + (0.5 * f(t,d))
                    --------------
                    max{ f(t,d) : t in d }

    where f(t,d) is the number of times t occurs in document d.
    """
    return 0.5 + (0.5 * document.count(term)) / max_frequency

def memoize(f):
    memo = {}
    def helper(t, *args):
        if t not in memo:
            memo[t] = f(t, *args)
        return memo[t]
    return helper 

@memoize
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
        term_set |= set(d)
    return list(term_set)

def vector_length(vec):
    return sqrt(sum([t*t for t in vec]))

def vectorize_document(document, document_list, unique_terms):
    """Returns a normalized vector representation of the document in the corpus space"""
    i = 0
    num = len(unique_terms)
    vec = []
    for t in unique_terms:
        vec.append(tf_idf(t, document, document_list))
        i += 1
        sys.stdout.write("\rtf-idf: {0:.2f}%    ({1}/{2})".format((i / num) * 100, i, num))
        sys.stdout.flush()

    vec_len = vector_length(vec)
    return [t/vec_len for t in vec]

def distance(vec1, vec2):
    """Calculate the distance between two document vectors"""
    assert len(vec1) == len(vec2)
    d = 0
    for v1,v2 in zip(vec1, vec2):
        d += (v1 - v2) ** 2
    return sqrt(d)

def reservoir_sample(arr, k):
    """Return k random samples of elements in arr"""
    reservoir = arr[:k]
    for i in range(k+1, len(arr)):
        j = randint(1, i)
        if j <= k:
            reservoir[j] = arr[i]
    return reservoir

def mean(arr):
    """Get mean value of an array"""
    return sum(arr) / len(arr)

def group_by_first(pairs):
    """Get a list of pairs that relates each unique key to a
       list of all values that are paired with that key."""
    keys = []
    for key, _ in pairs:
        if key not in keys:
            keys.append(key)
    return [[y for x, y in pairs if x == key] for key in keys]

def find_closest(doc_vector, centroids):
    """Find the closest centroid to a document vector"""
    return min(centroids, key=lambda centroid: distance(centroid, doc_vector))

def group_by_centroid(document_vectors, centroids):
    """Get a list of the closest document vectors for each centroid"""
    centroid_document_pairs = []
    for doc in document_vectors:
        doc_centroid = find_closest(doc, centroids)
        centroid_document_pairs.append([doc_centroid, doc])
    return group_by_first(centroid_document_pairs)

def find_centroid(cluster):
    """Get centroid of document vectors in cluster"""
    mid = []
    for i in range(len(cluster[0])):
        mid.append(mean([doc[i] for doc in cluster]))
    return mid

def k_means(document_vectors, k, max_updates=100):
    """Find k centroids for document_vectors clusters"""
    assert len(document_vectors) >= k, 'More clusters than documents'

    num_documents = len(document_vectors)
    # Choose k random documents for starting centroids
    old_centroids, n = [], 0
    centroids = reservoir_sample(document_vectors, k)
    # Continuusly update centroids based on mean position in its cluster
    while old_centroids != centroids and n < max_updates:
        old_centroids = centroids
        clusters = group_by_centroid(document_vectors, centroids)
        centroids = [find_centroid(cluster) for cluster in clusters]
        n += 1

    return centroids

def dot_product(vec1, vec2):
    return sum([u * v for u,v in zip(vec1, vec2)])

def similarity(doc_vec, query_vec):
    """Document relevance ranking as a measure of the angle between 
       the document vector and a vector representation of the keyword"""
    assert len(doc_vec) == len(query_vec), "Query vector size must match document vector size"
    
    return dot_product(doc_vec, query_vec) / (vector_length(doc_vec) * vector_length(query_vec))

