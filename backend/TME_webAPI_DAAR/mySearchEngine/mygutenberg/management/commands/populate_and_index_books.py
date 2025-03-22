from django.core.management.base import BaseCommand
import requests
import time
import re
from collections import defaultdict
from mygutenberg.models import BookText, TableJaccard, TrieNode
from mygutenberg.algorithms.tfidf import index_document
from mygutenberg.algorithms.jaccard import compute_jaccard_similarity
from mygutenberg.algorithms.centrality import build_graph, closeness_centrality, betweenness_centrality

class Command(BaseCommand):
    help = 'Remplit et indexe les livres Gutenberg, construit le Trie, et calcule les similarités Jaccard.'

    def handle(self, *args, **options):
        self.stdout.write(f"[{time.ctime()}] Début du remplissage et de l'indexation des livres...")

        # Configuration
        base_url = 'https://gutendex.com/books/'
        target_count = 1664  # Objectif final : 1664 livres
        threshold = 0.35  # Seuil pour Jaccard
        page = 1
        books_added = 0

        whitelists = {
            'en': 'words_alpha.txt',
            'fr': 'liste.de.mots.francais.frgut.txt'
        }
        languages = ['en', 'fr']
        all_docs = {}
        book_meta = {}

        # Chargement des listes blanches
        whitelist_data = {}
        for lang in languages:
            with open(whitelists[lang], 'r') as f:
                whitelist_data[lang] = set(line.strip().lower() for line in f if len(line.strip()) > 2)
            self.stdout.write(f"[{time.ctime()}] {len(whitelist_data[lang])} mots chargés pour {lang}.")

        # Réinitialisation des tables
        BookText.objects.all().delete()
        TrieNode.objects.all().delete()
        TableJaccard.objects.all().delete()

        # Récupération et traitement des livres
        while books_added < target_count:
            self.stdout.write(f"[{time.ctime()}] Récupération de la page {page}...")
            response = requests.get(f'{base_url}?page={page}&languages=fr,en')
            books = response.json().get('results', [])
            self.stdout.write(f"[{time.ctime()}] {len(books)} livres trouvés.")

            for book in books:
                book_id = book['id']
                if BookText.objects.filter(gutenberg_id=book_id).exists():
                    self.stdout.write(f"[{time.ctime()}] Livre {book_id} ignoré (déjà existant)")
                    continue

                language = book.get('languages', ['en'])[0]
                if language not in languages:
                    continue

                text_url = f'http://gutenberg.org/ebooks/{book_id}.txt.utf-8'
                try:
                    text_response = requests.get(text_url)
                    text_response.raise_for_status()
                    content = text_response.text.lower()
                    words = re.split(r'[^A-Za-z]+', content)
                    filtered_words = [w for w in words if w in whitelist_data[language] and len(w) > 2]

                    if 10000 <= len(filtered_words) <= 100000:
                        title = book.get('title', 'Unknown')
                        authors_list = [{'name': a.get('name', '')} for a in book.get('authors', [])]

                        all_docs[book_id] = filtered_words
                        book_meta[book_id] = {'title': title, 'authors': authors_list, 'language': language}

                        BookText.objects.create(
                            gutenberg_id=book_id,
                            title=title,
                            authors=authors_list,
                            word_count=len(filtered_words),
                            language=language,
                            closeness_centrality=0.0,
                            betweenness_centrality=0.0
                        )

                        books_added += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"[{time.ctime()}] Livre {book_id} ajouté ({len(filtered_words)} mots, {language}) - {books_added}/{target_count}"
                        ))

                        if books_added >= target_count:
                            break

                except requests.RequestException as e:
                    self.stdout.write(self.style.WARNING(f"[{time.ctime()}] Échec de récupération du livre {book_id} : {str(e)}"))
                    continue

            self.stdout.write(f"[{time.ctime()}] Page {page} terminée - Total livres ajoutés : {books_added}/{target_count}")
            page += 1

        self.stdout.write(f"[{time.ctime()}] Fin de la récupération. Total livres ajoutés : {books_added}")

        # Pré-calcul des fréquences de documents (DF)
        self.stdout.write(f"[{time.ctime()}] Calcul des fréquences de documents (DF)...")
        document_frequencies = defaultdict(int)
        for words in all_docs.values():
            for term in set(words):
                document_frequencies[term] += 1
        total_documents = len(all_docs)
        self.stdout.write(f"[{time.ctime()}] DF calculé pour {len(document_frequencies)} termes uniques sur {total_documents} documents.")

        # Étape d'indexation avec Trie
        self.stdout.write(f"[{time.ctime()}] Début de l'indexation pour {total_documents} livres...")
        books_processed = 0
        total_words_indexed = 0
        trie_nodes_to_create = []
        trie_nodes_dict = {} # Dictionnaire pour suivre les noeuds en mémoire (clé: (parent_id, char))

        for book_id, filtered_words in all_docs.items():
            books_processed += 1
            self.stdout.write(f"[{time.ctime()}] Indexation du livre {book_id} ({books_processed}/{total_documents})...")

            if book_id not in book_meta:
                self.stdout.write(self.style.WARNING(f"[{time.ctime()}] Métadonnées manquantes pour le livre {book_id}"))
                continue

            meta = book_meta[book_id]
            title_words = [w for w in re.split(r'[^A-Za-z]+', meta['title'].lower()) if w]
            author_words = []
            for author in meta['authors']:
                author_words.extend(w for w in re.split(r'[^A-Za-z]+', author['name'].lower()) if w)

            doc_index = index_document(
                document_words=filtered_words,
                total_documents=total_documents,
                document_frequencies=document_frequencies,
                title_words=title_words,
                author_words=author_words
            )

            for word, data in doc_index.items():
                total_words_indexed = insert_word_into_trie(
                    word, book_id, data, trie_nodes_dict, trie_nodes_to_create, total_words_indexed
                )

        self.stdout.write(f"[{time.ctime()}] Index construit avec {total_words_indexed} entrées au total.")

        self.stdout.write(f"[{time.ctime()}] Sauvegarde des noeuds dans la base...")
        if trie_nodes_to_create:
            save_trie_nodes(trie_nodes_to_create)
                
        self.stdout.write(self.style.SUCCESS(f"[{time.ctime()}] {books_added} livres indexés avec succès !"))

        # Calcul des similarités de Jaccard
        self.stdout.write(f"[{time.ctime()}] Calcul des similarités de Jaccard avec un seuil de {threshold}...")
        book_ids = list(all_docs.keys())
        similarities = compute_jaccard_similarity(book_ids, all_docs, threshold)

        # Remplissage de TableJaccard
        created_count = 0
        self.stdout.write(f"[{time.ctime()}] Enregistrement des similarités dans TableJaccard...")
        for (id1, id2), similarity in similarities.items():
            try:
                book1 = BookText.objects.get(gutenberg_id=id1)
                book2 = BookText.objects.get(gutenberg_id=id2)
                TableJaccard.objects.create(
                    book1=book1,
                    book2=book2,
                    jaccard_similarity=similarity
                )
                created_count += 1
                if created_count % 1000 == 0:
                    self.stdout.write(f"[{time.ctime()}] {created_count} similarités enregistrées...")
            except BookText.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"[{time.ctime()}] Livre {id1} ou {id2} non trouvé."))
                continue

        self.stdout.write(self.style.SUCCESS(f"[{time.ctime()}] {created_count} similarités enregistrées avec succès."))

        # Construire le graphe et calculer les centralités
        self.stdout.write(f"[{time.ctime()}] Construction du graphe et calcul des centralités...")
        graph = build_graph(TableJaccard.objects.all())
        if graph:
            books = BookText.objects.all()
            book_ids = [book.gutenberg_id for book in books]
            closeness = closeness_centrality(graph, book_ids)
            betweenness = betweenness_centrality(graph, book_ids)

            for book in books:
                book.closeness_centrality = closeness.get(book.gutenberg_id, 0.0)
                book.betweenness_centrality = betweenness.get(book.gutenberg_id, 0.0)
                book.save()

            self.stdout.write(self.style.SUCCESS(f"[{time.ctime()}] Centralités calculées et enregistrées dans BookText."))
        else:
            self.stdout.write(self.style.WARNING(f"[{time.ctime()}] Aucun graphe généré."))

        self.stdout.write(self.style.SUCCESS(f"[{time.ctime()}] {books_added} livres ajoutés, indexés, similarités et centralités calculées avec succès !"))

def insert_word_into_trie(word, book_id, data, trie_nodes_dict, trie_nodes_to_create, total_words_indexed):
    parent = None
    parent_id = None
    
    for char in word.lower():
        key = (parent_id, char)
        if key in trie_nodes_dict:
            node = trie_nodes_dict[key]
        else:
            node = TrieNode(parent=parent, char=char, is_end_of_word=False)
            trie_nodes_dict[key] = node
            trie_nodes_to_create.append(node)
        parent = node
        parent_id = id(node)
        
    if not parent.is_end_of_word:
        parent.is_end_of_word = True
        parent.set_word_data({book_id: data})
    else:
        existing_data = parent.get_word_data()
        existing_data[book_id] = data
        parent.set_word_data(existing_data)

    total_words_indexed += 1
    return total_words_indexed

def save_trie_nodes(trie_nodes_to_create):
    # Sauvegarder les noeuds racines (parent=None)
    root_nodes = [n for n in trie_nodes_to_create if n.parent is None]
    if root_nodes:
        TrieNode.objects.bulk_create(root_nodes, batch_size=1000)
    
    # Sauvegarder les noeuds enfants itérativement
    remaining_nodes = [n for n in trie_nodes_to_create if n.parent is not None]
    saved_nodes = {id(n): n for n in root_nodes}  # Dictionnaire des noeuds sauvegardés (id mémoire -> objet)
    
    while remaining_nodes:
        nodes_to_save = []
        still_pending = []
        
        for node in remaining_nodes:
            parent_memory_id = id(node.parent)
            if parent_memory_id in saved_nodes:
                node.parent_id = saved_nodes[parent_memory_id].pk  # Mettre à jour avec le vrai pk
                nodes_to_save.append(node)
            else:
                still_pending.append(node)
        
        if not nodes_to_save:
            print(f"[{time.ctime()}] ERREUR : Boucle infinie détectée, {len(remaining_nodes)} nœuds restants.")
            break
        
        TrieNode.objects.bulk_create(nodes_to_save, batch_size=1000)
        saved_nodes.update({id(n): n for n in nodes_to_save})
        remaining_nodes = still_pending