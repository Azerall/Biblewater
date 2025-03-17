import math

def compute_tf(term, document_words):
    """Calcule la fréquence d'un terme dans un document (occurrences / total mots)."""
    occurrences = document_words.count(term)
    return occurrences / len(document_words) if document_words else 0

def compute_idf(term, document_frequencies, total_documents):
    """Calcule l'IDF d'un terme avec DF pré-calculé."""
    df = document_frequencies.get(term, 0) + 1  # +1 pour éviter division par 0
    return math.log(total_documents / df)

def compute_tfidf(term, document_words, document_frequencies, total_documents):
    """Calcule le TF-IDF avec DF global."""
    tf = compute_tf(term, document_words)
    idf = compute_idf(term, document_frequencies, total_documents)
    return tf * idf

def index_document(document_words, total_documents, document_frequencies, title_words, author_words):
    """Indexe un document avec TF-IDF et poids pour titre/auteur."""
    index = {}
    for term in set(document_words):
        tfidf = compute_tfidf(term, document_words, document_frequencies, total_documents)
        score = tfidf
        if term in title_words:
            score *= 5  # Poids titre
        if term in author_words:
            score *= 10  # Poids auteur
        index[term] = {
            'occurrences': document_words.count(term),
            'tfidf': tfidf,
            'score': score
        }
    return index