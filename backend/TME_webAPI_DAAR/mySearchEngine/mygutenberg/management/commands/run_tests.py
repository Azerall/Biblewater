from django.core.management.base import BaseCommand
import time
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from mygutenberg.models import BookText, TableIndex, TableJaccard
from mygutenberg.algorithms.tfidf import index_document
from mygutenberg.algorithms.jaccard import compute_jaccard_similarity
from mygutenberg.algorithms.centrality import build_graph, closeness_centrality, betweenness_centrality, pagerank

class Command(BaseCommand):
    help = 'Run performance and relevance tests for mygutenberg algorithms with realistic book sizes'

    def handle(self, *args, **options):
        self.stdout.write("=== Tests de performance ===")
        sizes, tfidf_times, jaccard_times, closeness_times, betweenness_times, pagerank_times = performance_test()
        plot_performance(sizes, tfidf_times, jaccard_times, closeness_times, betweenness_times, pagerank_times)

        self.stdout.write("\n=== Tests de pertinence ===")
        relevance_test()

def get_testbed():
    books = BookText.objects.all()[:300]
    book_ids = [book.gutenberg_id for book in books]
    table_indices = TableIndex.objects.all()[:6000]
    return book_ids, table_indices

def performance_test():
    book_ids, table_indices = get_testbed()
    sizes = [10, 50, 100, 150, 200, 250, 300]
    tfidf_times, jaccard_times, closeness_times, betweenness_times, pagerank_times = [], [], [], [], []

    for size in sizes:
        sample_ids = book_ids[:size]
        sample_indices = table_indices[:int(size * 20)]

        # Simuler un livre avec 10 000 mots
        start = time.time()
        book = BookText.objects.get(gutenberg_id=sample_ids[0])
        base_words = book.title.split() if book.title and isinstance(book.title, str) else ["default"]
        doc_words = (base_words * (10000 // max(len(base_words), 1) + 1))[:10000]
        total_docs = len(book_ids)
        doc_freq = defaultdict(int, {word: 1 for word in set(doc_words)})
        title_words = doc_words[:5]
        author_words = doc_words[:2]
        index_document(doc_words, total_docs, doc_freq, title_words, author_words)
        tfidf_time = time.time() - start
        tfidf_times.append(tfidf_time)
        print(f"TF-IDF (size={size}): {tfidf_time:.4f}s")

        # Test Jaccard
        start = time.time()
        compute_jaccard_similarity(sample_ids, sample_indices)
        jaccard_time = time.time() - start
        jaccard_times.append(jaccard_time)
        print(f"Jaccard (size={size}): {jaccard_time:.4f}s")

        # Construire le graphe
        jaccard_entries = TableJaccard.objects.filter(book1_id__in=sample_ids, book2_id__in=sample_ids)
        graph = build_graph(jaccard_entries)

        # Test Closeness Centrality
        start = time.time()
        closeness_centrality(graph, sample_ids)
        closeness_time = time.time() - start
        closeness_times.append(closeness_time)
        print(f"Closeness (size={size}): {closeness_time:.4f}s")

        # Test Betweenness Centrality
        start = time.time()
        betweenness_centrality(graph, sample_ids)
        betweenness_time = time.time() - start
        betweenness_times.append(betweenness_time)
        print(f"Betweenness (size={size}): {betweenness_time:.4f}s")

        # Test PageRank
        start = time.time()
        pagerank(graph, sample_ids)
        pagerank_time = time.time() - start
        pagerank_times.append(pagerank_time)
        print(f"PageRank (size={size}): {pagerank_time:.4f}s")

    return sizes, tfidf_times, jaccard_times, closeness_times, betweenness_times, pagerank_times

def relevance_test():
    book_ids, table_indices = get_testbed()
    sample_ids = book_ids[:10]
    
    # TF-IDF avec 10 000 mots
    book = BookText.objects.get(gutenberg_id=sample_ids[0])
    base_words = book.title.split() if book.title and isinstance(book.title, str) else ["default"]
    doc_words = (base_words * (10000 // max(len(base_words), 1) + 1))[:10000]
    total_docs = len(book_ids)
    doc_freq = defaultdict(int, {word: 1 for word in set(doc_words)})
    index = index_document(doc_words, total_docs, doc_freq, doc_words[:5], doc_words[:2])
    top_terms = sorted(index.items(), key=lambda x: x[1]['score'], reverse=True)[:5]
    print("Top 5 termes TF-IDF :", [(term, data['score']) for term, data in top_terms])

    # Jaccard
    similarities = compute_jaccard_similarity(sample_ids, table_indices)
    top_pairs = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:5]
    print("Top 5 paires Jaccard :", [(pair, sim) for pair, sim in top_pairs])

def plot_performance(sizes, tfidf_times, jaccard_times, closeness_times, betweenness_times, pagerank_times):
    # Graphique 1 : TF-IDF
    plt.figure(figsize=(8, 5))
    plt.plot(sizes, tfidf_times, label="TF-IDF", marker='o', color='blue')
    plt.xlabel("Taille de l'échantillon (livres)")
    plt.ylabel("Temps d'exécution (secondes)")
    plt.title("Performance de TF-IDF (10 000 mots par livre)")
    plt.legend()
    plt.grid(True)
    plt.savefig("tfidf_performance.png")
    plt.show()

    # Graphique 2 : Jaccard
    plt.figure(figsize=(8, 5))
    plt.plot(sizes, jaccard_times, label="Jaccard", marker='o', color='green')
    plt.xlabel("Taille de l'échantillon (livres)")
    plt.ylabel("Temps d'exécution (secondes)")
    plt.title("Performance de Jaccard")
    plt.legend()
    plt.grid(True)
    plt.savefig("jaccard_performance.png")
    plt.show()

    # Graphique 3 : Centralités
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, closeness_times, label="Closeness Centrality", marker='o', color='orange')
    plt.plot(sizes, betweenness_times, label="Betweenness Centrality", marker='o', color='red')
    plt.plot(sizes, pagerank_times, label="PageRank", marker='o', color='purple')
    plt.xlabel("Taille de l'échantillon (livres)")
    plt.ylabel("Temps d'exécution (secondes)")
    plt.title("Performance des Centralités")
    plt.legend()
    plt.grid(True)
    plt.savefig("centralities_performance.png")
    plt.show()

    # Diagramme en bâtons avec moyenne et écart-type
    times = [tfidf_times, jaccard_times, closeness_times, betweenness_times, pagerank_times]
    labels = ["TF-IDF", "Jaccard", "Closeness", "Betweenness", "PageRank"]
    means = [np.mean(t) for t in times]
    stds = [np.std(t) for t in times]
    
    plt.figure(figsize=(10, 6))
    plt.bar(labels, means, yerr=stds, capsize=5, color=['blue', 'green', 'orange', 'red', 'purple'])
    plt.yscale('log')
    plt.ylabel("Temps moyen (secondes, échelle log)")
    plt.title("Temps moyen et écart-type des algorithmes")
    plt.savefig("performance_bar_log.png")
    plt.show()
    
