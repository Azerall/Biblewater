from django.core.management.base import BaseCommand
import time
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import os
import requests
import re
from mygutenberg.models import BookText, TrieNode, TableJaccard
from mygutenberg.algorithms.tfidf import index_document
from mygutenberg.algorithms.jaccard import compute_jaccard_similarity
from mygutenberg.algorithms.centrality import build_graph, closeness_centrality, betweenness_centrality
from mygutenberg.algorithms.automaton import build_dfa_from_regex

class Command(BaseCommand):
    help = 'Exécute les tests de performance et génère des graphiques'

    def handle(self, *args, **options):
        if not os.path.exists('graphs'):
            os.makedirs('graphs')

        # Testbed pour recherche et centralités (basé sur nombre de livres)
        book_ids, all_docs, index_array, trie_root = get_testbed(max_books=200)

        # Testbed spécifique pour TF-IDF (basé sur nombre de mots)
        tfidf_book_ids, tfidf_docs = get_tfidf_testbed()

        print("Démarrage des tests de performance de TF-IDF et centralités...")
        sizes, tfidf_sizes, tfidf_times, jaccard_times, closeness_times, betweenness_times = performance_test(book_ids, all_docs, tfidf_book_ids, tfidf_docs)
        print("Tests de performance terminés, génération des graphiques...")
        plot_performance(sizes, tfidf_sizes, tfidf_times, jaccard_times, closeness_times, betweenness_times)

        print("Démarrage des tests de performance de recherche...")
        sizes, trie_times, index_times = search_performance_test(book_ids, index_array, trie_root)
        print("Tests terminés, génération des graphiques...")
        plot_search_performance(sizes, trie_times, index_times)

        print("Tests terminés !")

class TempTrieNode:
    def __init__(self, char='', parent=None):
        self.char = char
        self.parent = parent
        self.children = {}
        self.is_end_of_word = False
        self.word_data = {}

    def set_word_data(self, data):
        self.word_data = data

    def get_word_data(self):
        return self.word_data

    def search_by_prefix(self, prefix):
        current_node = self
        for char in prefix.lower():
            if char not in current_node.children:
                return []
            current_node = current_node.children[char]
        results = []
        self._collect_words(current_node, results, prefix)
        return results

    def _collect_words(self, node, results, prefix):
        if node.is_end_of_word:
            results.append({'word': prefix, 'data': node.get_word_data()})
        for char, child in node.children.items():
            self._collect_words(child, results, prefix + char)

    def traverse_with_dfa(self, dfa, current_word='', results=None, state=None):
        if results is None:
            results = defaultdict(lambda: {'score': 0.0, 'matches': 0})
        if state is None:
            state = dfa.start_state
        
        if self.char:
            current_state = dfa.transition(state, self.char)
            if current_state == -1:
                return results

            current_word += self.char
            if dfa.is_accepting(current_state) and self.is_end_of_word:
                word_data = self.get_word_data()
                for book_id, data in word_data.items():
                    occurrences = data.get('occurrences', 1)
                    score = data.get('score', 0.0)
                    results[book_id]['matches'] += occurrences
                    results[book_id]['score'] += score
        else:
            current_state = state

        for char, child in self.children.items():
            next_state = dfa.transition(current_state, char)
            if next_state != -1:
                child.traverse_with_dfa(dfa, current_word, results, current_state)

        return results

def get_testbed(max_books):
    print("Construction du testbed...")
    start_time = time.time()

    books = BookText.objects.filter(language='en').order_by('?')[:max_books * 2]
    book_ids = []
    for book in books:
        if len(book_ids) >= max_books:
            break
        if book.gutenberg_id not in book_ids:
            book_ids.append(book.gutenberg_id)
    print(f"{len(book_ids)} livres sélectionnés pour le testbed.")

    whitelist = set()
    try:
        with open('words_alpha.txt', 'r') as f:
            whitelist = set(line.strip().lower() for line in f if len(line.strip()) > 2)
        print(f"{len(whitelist)} mots chargés dans la whitelist.")
    except FileNotFoundError:
        print("Whitelist non trouvée.")

    all_docs = {}
    for book_id in book_ids:
        if book_id not in all_docs:
            text_url = f'http://gutenberg.org/ebooks/{book_id}.txt.utf-8'
            try:
                print(f"  Téléchargement du livre {book_id}... {len(all_docs)+1}/{len(book_ids)}")
                response = requests.get(text_url, timeout=10)
                response.raise_for_status()
                content = response.text.lower()
                words = re.split(r'[^A-Za-z]+', content)
                filtered_words = [w for w in words if w in whitelist or not whitelist]
                if 10000 <= len(filtered_words) <= 100000:
                    all_docs[book_id] = filtered_words
            except requests.RequestException as e:
                print(f"  Échec pour {book_id} : {str(e)}.")

    # Construire le tableau d'index
    print("Construction du tableau d'index pour les tests...")
    index_array = defaultdict(lambda: defaultdict(dict))
    for book_id, words in all_docs.items():
        total_docs = len(all_docs)
        doc_freq = defaultdict(int)
        for word in set(words):
            doc_freq[word] += 1
        word_counts = defaultdict(int)
        for word in words:
            word_counts[word] += 1
        for word, count in word_counts.items():
            tf = count / len(words)
            idf = np.log(total_docs / (doc_freq[word] + 1)) + 1
            score = tf * idf
            index_array[word][book_id] = {'score': score, 'occurrences': count}

    # Construire un TrieNode temporaire en mémoire
    print("Construction du TrieNode temporaire pour les tests...")
    trie_root = TempTrieNode()
    for book_id, words in all_docs.items():
        total_docs = len(all_docs)
        doc_freq = defaultdict(int)
        for word in set(words):
            doc_freq[word] += 1
        word_counts = defaultdict(int)
        for word in words:
            word_counts[word] += 1
        for word, count in word_counts.items():
            tf = count / len(words)
            idf = np.log(total_docs / (doc_freq[word] + 1)) + 1
            score = tf * idf
            current_node = trie_root
            for char in word:
                if char not in current_node.children:
                    current_node.children[char] = TempTrieNode(char, current_node)
                current_node = current_node.children[char]
            current_node.is_end_of_word = True
            current_node.set_word_data({book_id: {'score': score, 'occurrences': count}})

    print(f"Testbed construit en {time.time() - start_time:.2f}s")
    return book_ids, all_docs, index_array, trie_root

def get_tfidf_testbed():
    print("Construction du testbed pour TF-IDF basé sur le nombre de mots...")
    start_time = time.time()

    books = BookText.objects.filter(language='en').order_by('?')
    book_ids = []
    all_docs = {}
    
    whitelist = set()
    try:
        with open('words_alpha.txt', 'r') as f:
            whitelist = set(line.strip().lower() for line in f if len(line.strip()) > 2)
        print(f"{len(whitelist)} mots chargés dans la whitelist.")
    except FileNotFoundError:
        print("Whitelist non trouvée.")

    target_ranges = [
        (10000, 20000), (20000, 30000), (30000, 40000), (40000, 50000),
        (50000, 60000), (60000, 70000), (70000, 80000), (80000, 90000), (90000, 100000)
    ]
    books_per_range = 5  # Objectif : 5 livres par intervalle
    range_counts = {range_tuple: 0 for range_tuple in target_ranges}

    for book in books:
        # Arrêter si chaque plage a ses 5 livres
        if all(count >= books_per_range for count in range_counts.values()):
            break
        
        book_id = book.gutenberg_id
        if book_id not in book_ids:
            text_url = f'http://gutenberg.org/ebooks/{book_id}.txt.utf-8'
            try:
                response = requests.get(text_url, timeout=10)
                response.raise_for_status()
                content = response.text.lower()
                words = re.split(r'[^A-Za-z]+', content)
                filtered_words = [w for w in words if w in whitelist or not whitelist]
                word_count = len(filtered_words)
                
                # Vérifier si le livre entre dans une plage cible avec de la place
                for min_words, max_words in target_ranges:
                    if min_words <= word_count <= max_words and range_counts[(min_words, max_words)] < books_per_range:
                        all_docs[book_id] = filtered_words
                        book_ids.append(book_id)
                        range_counts[(min_words, max_words)] += 1
                        print(f"  Livre {book_id} ajouté dans la plage {min_words}-{max_words}. {len(all_docs)} livres trouvés.")
                        break
            except requests.RequestException as e:
                print(f"  Échec pour {book_id} : {str(e)}.")

    return book_ids, all_docs

def performance_test(book_ids, all_docs, tfidf_book_ids, tfidf_docs):
    print("Début de performance_test...")
    sizes = [10, 25, 50, 75, 100, 125, 150, 175, 200]  # Tailles pour centralités/Jaccard
    tfidf_size_ranges = [
        (10000, 20000), (20000, 30000), (30000, 40000), (40000, 50000),
        (50000, 60000), (60000, 70000), (70000, 80000), (80000, 90000), (90000, 100000)
    ]
    tfidf_times, jaccard_times, closeness_times, betweenness_times = [], [], [], []

    # Test TF-IDF basé sur les plages de mots
    print("Test TF-IDF par plages de nombre de mots...")
    for min_words, max_words in tfidf_size_ranges:
        print(f"Traitement TF-IDF pour la plage {min_words}-{max_words} mots...")
        tfidf_avg = []
        for book_id in tfidf_book_ids:
            doc_words = tfidf_docs[book_id]
            word_count = len(doc_words)
            if min_words <= word_count <= max_words:
                start = time.time()
                total_docs = len(tfidf_docs)
                doc_freq = defaultdict(int, {word: 1 for word in set(doc_words)})
                title_words = doc_words[:5]
                author_words = doc_words[:2]
                index_document(doc_words, total_docs, doc_freq, title_words, author_words)
                tfidf_avg.append(time.time() - start)
        if tfidf_avg:
            tfidf_times.append(np.mean(tfidf_avg))
            print(f"  TF-IDF pour {min_words}-{max_words} mots: {tfidf_times[-1]:.4f}s")
        else:
            tfidf_times.append(0.0)  # Placeholder si aucun livre dans la plage
            print(f"  Aucun livre trouvé dans la plage {min_words}-{max_words} mots")

    # Tests Jaccard et centralités basés sur le nombre de livres
    for size in sizes:
        print(f"\nTraitement de l'échantillon de taille {size} livres...")
        sample_ids = book_ids[:size]
        if len(sample_ids) < size:
            print(f"Pas assez de livres pour la taille {size}, utilisation de {len(sample_ids)} livres.")
        
        jaccard_avg, closeness_avg, betweenness_avg = [], [], []

        # Jaccard
        print(f"  Calcul de Jaccard pour la taille {size}...")
        start = time.time()
        compute_jaccard_similarity(sample_ids, {bid: all_docs[bid] for bid in sample_ids}, threshold=0.35)
        jaccard_avg.append(time.time() - start)

        # Centralités
        print(f"  Construction du graphe pour la taille {size}...")
        start = time.time()
        jaccard_entries = TableJaccard.objects.filter(book1_id__in=sample_ids, book2_id__in=sample_ids)
        graph = build_graph(jaccard_entries)

        start = time.time()
        closeness_centrality(graph, sample_ids)
        closeness_avg.append(time.time() - start)

        start = time.time()
        betweenness_centrality(graph, sample_ids)
        betweenness_avg.append(time.time() - start)

        jaccard_times.append(np.mean(jaccard_avg))
        closeness_times.append(np.mean(closeness_avg))
        betweenness_times.append(np.mean(betweenness_avg))

        print(f"Résultats pour taille {size}:")
        print(f"  Jaccard: {jaccard_times[-1]:.4f}s")
        print(f"  Closeness: {closeness_times[-1]:.4f}s")
        print(f"  Betweenness: {betweenness_times[-1]:.4f}s")

    return sizes, tfidf_size_ranges, tfidf_times, jaccard_times, closeness_times, betweenness_times

def plot_performance(sizes, tfidf_size_ranges, tfidf_times, jaccard_times, closeness_times, betweenness_times):
    print("Génération des graphiques...")
    
    # TF-IDF par plages de nombre de mots
    tfidf_labels = [f"{min_w}-{max_w}" for min_w, max_w in tfidf_size_ranges]
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(tfidf_labels)), tfidf_times, label="TF-IDF", marker='o', color='blue')
    plt.xticks(range(len(tfidf_labels)), tfidf_labels, rotation=45)
    plt.xlabel("Plage de nombre de mots dans le livre")
    plt.ylabel("Temps d'exécution moyen (secondes)")
    plt.title("Performance de TF-IDF par taille de texte")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("graphs/tfidf_performance_by_words.png")
    plt.show()

    # Jaccard par nombre de livres
    plt.figure(figsize=(8, 5))
    plt.plot(sizes, jaccard_times, label="Jaccard", marker='o', color='green')
    plt.xlabel("Taille de l'échantillon (nombre de livres)")
    plt.ylabel("Temps d'exécution (secondes)")
    plt.title("Performance de Jaccard")
    plt.legend()
    plt.grid(True)
    plt.savefig("graphs/jaccard_performance.png")
    plt.show()

    # Centralités par nombre de livres
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, closeness_times, label="Closeness Centrality", marker='o', color='orange')
    plt.plot(sizes, betweenness_times, label="Betweenness Centrality", marker='o', color='red')
    plt.xlabel("Taille de l'échantillon (nombre de livres)")
    plt.ylabel("Temps d'exécution (secondes)")
    plt.title("Performance des Centralités")
    plt.legend()
    plt.grid(True)
    plt.savefig("graphs/centralities_performance.png")
    plt.show()

    # Diagramme en barres (sans TF-IDF)
    times = [jaccard_times, closeness_times, betweenness_times]
    labels = ["Jaccard", "Closeness", "Betweenness"]
    means = [np.mean(t) for t in times]
    stds = [np.std(t) for t in times]
    
    plt.figure(figsize=(10, 6))
    plt.bar(labels, means, yerr=stds, capsize=5, color=['green', 'orange', 'red', 'purple'])
    plt.yscale('log')
    plt.ylabel("Temps moyen (secondes, échelle log)")
    plt.title("Temps moyen et écart-type des algorithmes (Jaccard et Centralités)")
    plt.savefig("graphs/performance_bar_log.png")
    plt.show()
    print("Graphiques générés.")

def search_by_keyword_exact_trie(keywords, book_ids, trie_root):
    aggregated_results = defaultdict(lambda: {'score': 0.0, 'occurrences': 0})
    for kw in keywords:
        current_node = trie_root
        for char in kw.lower():
            if char not in current_node.children:
                break
            current_node = current_node.children[char]
        else:
            if current_node.is_end_of_word:
                word_data = current_node.get_word_data()
                for book_id, data in word_data.items():
                    if book_id in book_ids:
                        aggregated_results[book_id]['score'] += data['score']
                        aggregated_results[book_id]['occurrences'] += data['occurrences']
    return aggregated_results

def search_by_keyword_exact_index(keywords, book_ids, index_array):
    aggregated_results = defaultdict(lambda: {'score': 0.0, 'occurrences': 0})
    for kw in keywords:
        if kw in index_array:
            for book_id, data in index_array[kw].items():
                if book_id in book_ids:
                    aggregated_results[book_id]['score'] += data['score']
                    aggregated_results[book_id]['occurrences'] += data['occurrences']
    return aggregated_results

def search_by_keyword_trie(keywords, book_ids, trie_root):
    aggregated_results = defaultdict(lambda: {'score': 0.0, 'occurrences': 0})
    for kw in keywords:
        prefix_results = trie_root.search_by_prefix(kw)
        for result in prefix_results:
            word_data = result['data']
            for book_id, data in word_data.items():
                if book_id in book_ids:
                    aggregated_results[book_id]['score'] += data['score']
                    aggregated_results[book_id]['occurrences'] += data['occurrences']
    return aggregated_results

def search_by_keyword_index(keywords, book_ids, index_array):
    aggregated_results = defaultdict(lambda: {'score': 0.0, 'occurrences': 0})
    for kw in keywords:
        for word in index_array:
            if word.startswith(kw):
                for book_id, data in index_array[word].items():
                    if book_id in book_ids:
                        aggregated_results[book_id]['score'] += data['score']
                        aggregated_results[book_id]['occurrences'] += data['occurrences']
    return aggregated_results

def search_by_regex_trie(regex, book_ids, trie_root):
    try:
        dfa = build_dfa_from_regex(regex)
        if not dfa:
            return {}
        results = trie_root.traverse_with_dfa(dfa)
        filtered_results = {bid: data for bid, data in results.items() if bid in book_ids}
        return filtered_results
    except Exception as e:
        print(f"Erreur regex Trie: {str(e)}")
        return {}

def search_performance_test(book_ids, index_array, trie_root):
    sizes = [1, 5, 10, 15, 20]  # Nombre de mots-clés
    trie_times = {'keyword_exact': [], 'keyword': [], 'regex': []}
    index_times = {'keyword_exact': [], 'keyword': [], 'regex': []}

    # Liste de mots-clés pour construire des requêtes de taille croissante
    all_keywords = ["the", "love", "advent", "waterfall", "time", "war", "peace", 
                    "river", "mountain", "journey", "life", "death", "hope", 
                    "dream", "fear", "light", "dark", "sky", "earth", "wind"]
    all_regexes = [
        "water", "water.*", "w.*ter", "w.*ter.*", ".*w.*t",
        "alice", ".alice", "..alice", "alice.*", ".*alice",
        "love", "love.*", "l.*ve", "l.*ve.*", ".*l.*v",
        "hope", "hope.*", "h.*pe", "h.*pe.*", ".*h.*p",
    ]

    for size in sizes:
        test_keywords = all_keywords[:size]
        print(f"\nTest avec {size} mots-clés...")

        # Test SearchByKeywordExact (mot exact)
        start = time.time()
        search_by_keyword_exact_trie(test_keywords, book_ids, trie_root)
        trie_times['keyword_exact'].append(time.time() - start)
        start = time.time()
        search_by_keyword_exact_index(test_keywords, book_ids, index_array)
        index_times['keyword_exact'].append(time.time() - start)
        print(f"  SearchByKeywordExact - Trie: {trie_times['keyword_exact'][-1]:.4f}s, Index: {index_times['keyword_exact'][-1]:.4f}s")

        # Test SearchByKeyword (préfixe)
        start = time.time()
        search_by_keyword_trie(test_keywords, book_ids, trie_root)
        trie_times['keyword'].append(time.time() - start)
        start = time.time()
        search_by_keyword_index(test_keywords, book_ids, index_array)
        index_times['keyword'].append(time.time() - start)
        print(f"  SearchByKeyword - Trie: {trie_times['keyword'][-1]:.4f}s, Index: {index_times['keyword'][-1]:.4f}s")

        # Test SearchByRegex
        trie_avg = []
        for regex in all_regexes[:size]:
            start = time.time()
            search_by_regex_trie(regex, book_ids, trie_root)
            trie_avg.append(time.time() - start)
        trie_times['regex'].append(np.mean(trie_avg))
        
        index_avg = []
        for regex in all_regexes[:size]:
            start = time.time()
            results = defaultdict(lambda: {'score': 0.0, 'matches': 0})
            for word in index_array:
                if re.match(regex, word):
                    for book_id, data in index_array[word].items():
                        if book_id in book_ids:
                            results[book_id]['score'] += data['score']
                            results[book_id]['matches'] += data['occurrences']
            index_avg.append(time.time() - start)
        index_times['regex'].append(np.mean(index_avg))
        print(f"  SearchByRegex - Trie: {trie_times['regex'][-1]:.4f}s, Index: {index_times['regex'][-1]:.4f}s")

    return sizes, trie_times, index_times

def plot_search_performance(sizes, trie_times, index_times):
    print("Génération des graphiques...")
    for search_type in ['keyword_exact', 'keyword', 'regex']:
        plt.figure(figsize=(8, 5))
        plt.plot(sizes, trie_times[search_type], label="TrieNode", marker='o', color='blue')
        plt.plot(sizes, index_times[search_type], label="Index Array", marker='o', color='green')
        plt.xlabel("Nombre de mots-clés")
        plt.ylabel("Temps d'exécution (secondes)")
        plt.title(f"Performance de {search_type.capitalize()} Search")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"graphs/{search_type}_performance.png")
        plt.show()

    labels = ['keyword_exact', 'keyword', 'regex']
    trie_means = [np.mean(trie_times[t.lower()]) for t in labels]
    index_means = [np.mean(index_times[t.lower()]) for t in labels]
    plt.figure(figsize=(10, 6))
    x = np.arange(len(labels))
    width = 0.35
    plt.bar(x - width/2, trie_means, width, label='TrieNode', color='blue')
    plt.bar(x + width/2, index_means, width, label='Index Array', color='green')
    plt.xlabel("Type de recherche")
    plt.ylabel("Temps moyen (secondes)")
    plt.title("Comparaison globale des performances")
    plt.xticks(x, labels)
    plt.legend()
    plt.savefig("graphs/search_comparison.png")
    plt.show()
    print("Graphiques générés.")