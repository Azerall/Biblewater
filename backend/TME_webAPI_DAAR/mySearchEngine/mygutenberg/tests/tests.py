import time
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from mygutenberg.models import BookText, TableIndex, TableJaccard
from mygutenberg.algorithms.tfidf import compute_tfidf, index_document
from mygutenberg.algorithms.jaccard import compute_jaccard_similarity
from mygutenberg.algorithms.centrality import build_graph, closeness_centrality, betweenness_centrality, pagerank

def get_testbed():
    books = BookText.objects.all()[:50]  # 50 livres pour les tests
    book_ids = [book.gutenberg_id for book in books]
    table_indices = TableIndex.objects.all()[:1000]  #  1000 mots pour la performance
    return book_ids, table_indices

def performance_test():
    book_ids, table_indices = get_testbed()
    sizes = [10, 20, 30, 40, 50]  # Tailles croissantes de l'échantillon
    tfidf_times, jaccard_times, centrality_times = [], [], []

    for size in sizes:
        sample_ids = book_ids[:size]
        sample_indices = table_indices[:int(size * 20)]  # Ajuster proportionnellement

        # Test TF-IDF
        start = time.time()
        doc_words = list(BookText.objects.get(gutenberg_id=sample_ids[0]).title.split()) * 100  # Simuler un document
        total_docs = len(book_ids)
        doc_freq = defaultdict(int, {word: 1 for word in set(doc_words)})
        index_document(doc_words, total_docs, doc_freq, doc_words[:5], doc_words[:2])
        tfidf_times.append(time.time() - start)

        # Test Jaccard
        start = time.time()
        compute_jaccard_similarity(sample_ids, sample_indices)
        jaccard_times.append(time.time() - start)

        # Test Centralités
        start = time.time()
        jaccard_entries = TableJaccard.objects.filter(book1_id__in=sample_ids, book2_id__in=sample_ids)
        graph = build_graph(jaccard_entries)
        closeness_centrality(graph, sample_ids)
        betweenness_centrality(graph, sample_ids)
        pagerank(graph, sample_ids)
        centrality_times.append(time.time() - start)

    return sizes, tfidf_times, jaccard_times, centrality_times

# 3. Test de pertinence
def relevance_test():
    """Évalue la pertinence des résultats TF-IDF et Jaccard."""
    book_ids, table_indices = get_testbed()
    sample_ids = book_ids[:10]
    
    # TF-IDF : Vérifier si les mots-clés pertinents ont des scores élevés
    doc_words = list(BookText.objects.get(gutenberg_id=sample_ids[0]).title.split()) * 100
    total_docs = len(book_ids)
    doc_freq = defaultdict(int, {word: 1 for word in set(doc_words)})
    index = index_document(doc_words, total_docs, doc_freq, doc_words[:5], doc_words[:2])
    top_terms = sorted(index.items(), key=lambda x: x[1]['score'], reverse=True)[:5]
    print("Top 5 termes TF-IDF :", [(term, data['score']) for term, data in top_terms])

    # Jaccard : Vérifier si les paires similaires sont cohérentes
    similarities = compute_jaccard_similarity(sample_ids, table_indices)
    top_pairs = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:5]
    print("Top 5 paires Jaccard :", [(pair, sim) for pair, sim in top_pairs])

# 4. Visualisation des performances
def plot_performance(sizes, tfidf_times, jaccard_times, centrality_times):
    """Génère des courbes de performance."""
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, tfidf_times, label="TF-IDF", marker='o')
    plt.plot(sizes, jaccard_times, label="Jaccard", marker='o')
    plt.plot(sizes, centrality_times, label="Centralités", marker='o')
    plt.xlabel("Taille de l'échantillon (livres)")
    plt.ylabel("Temps d'exécution (secondes)")
    plt.title("Performance des algorithmes")
    plt.legend()
    plt.grid(True)
    plt.savefig("performance_plot.png")
    plt.show()

    # Diagrammes en bâtons avec moyenne et écart-type
    times = [tfidf_times, jaccard_times, centrality_times]
    labels = ["TF-IDF", "Jaccard", "Centralités"]
    means = [np.mean(t) for t in times]
    stds = [np.std(t) for t in times]
    
    plt.figure(figsize=(8, 5))
    plt.bar(labels, means, yerr=stds, capsize=5, color=['blue', 'green', 'orange'])
    plt.ylabel("Temps moyen (secondes)")
    plt.title("Temps moyen et écart-type")
    plt.savefig("performance_bar.png")
    plt.show()

# Exécution des tests
if __name__ == "__main__":
    print("=== Tests de performance ===")
    sizes, tfidf_times, jaccard_times, centrality_times = performance_test()
    plot_performance(sizes, tfidf_times, jaccard_times, centrality_times)

    print("\n=== Tests de pertinence ===")
    relevance_test()