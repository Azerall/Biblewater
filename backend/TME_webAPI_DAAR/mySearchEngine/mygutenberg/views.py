import requests
import re
from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from django.db import models
from mygutenberg.models import BookText, TrieNode, TableJaccard
from mygutenberg.clean_content import nettoyer_texte
from mygutenberg.algorithms.automaton import build_dfa_from_regex

class BooksList(APIView):
    def get(self, request, format=None):
        books = BookText.objects.all()
        return Response([{
            'id': book.gutenberg_id,
            'title': book.title,
            'authors': book.authors,
            'language': book.language,
            'cover_url': f'https://gutenberg.org/files/{book.gutenberg_id}/{book.gutenberg_id}-h/images/cover.jpg',
        } for book in books])

class BookDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            book = BookText.objects.get(gutenberg_id=pk)
            text_url = f'http://gutenberg.org/ebooks/{pk}.txt.utf-8'
            content = requests.get(text_url).text
            return Response({
                'id': book.gutenberg_id,
                'title': book.title,
                'authors': book.authors,
                'language': book.language,
                'cover_url': f'https://gutenberg.org/files/{book.gutenberg_id}/{book.gutenberg_id}-h/images/cover.jpg',
                'content': nettoyer_texte(content)
            })
        except BookText.DoesNotExist:
            raise Http404
        except requests.RequestException:
            return Response({'error': 'Unable to fetch content'}, status=500)

class FrenchBooksList(APIView):
    def get(self, request, format=None):
        books = BookText.objects.filter(language='fr')
        return Response([{
            'id': book.gutenberg_id,
            'title': book.title,
            'authors': book.authors,
            'language': book.language,
            'cover_url': f'https://gutenberg.org/files/{book.gutenberg_id}/{book.gutenberg_id}-h/images/cover.jpg',
        } for book in books])

class EnglishBooksList(APIView):
    def get(self, request, format=None):
        books = BookText.objects.filter(language='en')
        return Response([{
            'id': book.gutenberg_id,
            'title': book.title,
            'authors': book.authors,
            'language': book.language,
            'cover_url': f'https://gutenberg.org/files/{book.gutenberg_id}/{book.gutenberg_id}-h/images/cover.jpg',
        } for book in books])

class SearchByKeyword(APIView):
    def get(self, request, keyword, format=None):
        keyword = keyword.lower().strip()
        keywords = [k.strip() for k in re.split(r'[+\s,;/]+', keyword) if k.strip()]
        
        if not keywords:
            return Response([])

        # Dictionnaire pour agréger les résultats par livre
        aggregated_results = defaultdict(lambda: {'score': 0.0, 'occurrences': 0})
        
        # Rechercher chaque préfixe dans TrieNode
        for kw in keywords:
            prefix_results = TrieNode.search_by_prefix(kw)
            for result in prefix_results:
                word_data = result['data']  # {book_id: {occurrences, tfidf, score}}
                for book_id, data in word_data.items():
                    aggregated_results[book_id]['score'] += data['score']
                    aggregated_results[book_id]['occurrences'] += data['occurrences']

        if not aggregated_results:
            return Response([])  # Aucun résultat trouvé pour tous les préfixes

        # Construire la liste des résultats
        results = []
        for book_id in aggregated_results:
            try:
                book = BookText.objects.get(gutenberg_id=book_id)
                results.append({
                    'id': book.gutenberg_id,
                    'title': book.title,
                    'authors': book.authors,
                    'language': book.language,
                    'cover_url': f'https://gutenberg.org/files/{book.gutenberg_id}/{book.gutenberg_id}-h/images/cover.jpg',
                    'score': aggregated_results[book_id]['score'],  # Score agrégé
                    'occurrences': aggregated_results[book_id]['occurrences']  # Occurrences totales
                })
            except BookText.DoesNotExist:
                continue  # Ignorer si le livre n'existe pas

        # Trier les résultats par score décroissant
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        return Response(results)

class SearchByRegex(APIView):
    def get(self, request, regex, format=None):
        try:
            dfa = build_dfa_from_regex(regex)
            if not dfa:
                raise Http404("Invalid regex or DFA construction failed")

            root_nodes = TrieNode.objects.filter(parent__isnull=True).prefetch_related('children')

            results = defaultdict(lambda: {'score': 0.0, 'matches': 0})
            for root in root_nodes:
                self._traverse_with_dfa(root, dfa, '', results)

            if not results:
                return Response([])

            result_list = []
            for book_id in results:
                try:
                    book = BookText.objects.get(gutenberg_id=book_id)
                    result_list.append({
                        'id': book.gutenberg_id,
                        'title': book.title,
                        'authors': book.authors,
                        'language': book.language,
                        'cover_url': f'https://gutenberg.org/files/{book.gutenberg_id}/{book.gutenberg_id}-h/images/cover.jpg',
                        'score': results[book_id]['score'],
                        'matches': results[book_id]['matches']
                    })
                except BookText.DoesNotExist:
                    continue

            result_list = sorted(result_list, key=lambda x: x['score'], reverse=True)
            return Response(result_list)

        except Exception as e:
            raise Http404(f"Invalid regex: {str(e)}")

    @staticmethod
    def _traverse_with_dfa(node, dfa, current_word, results, state=None):
        if state is None:
            state = dfa.start_state
        current_word += node.char
        current_state = dfa.transition(state, node.char)

        if dfa.is_accepting(current_state) and node.is_end_of_word:
            word_data = node.get_word_data()
            for book_id, data in word_data.items():
                occurrences = data.get('occurrences', 1)
                score = data.get('score', 0.0)
                results[book_id]['matches'] += occurrences
                results[book_id]['score'] += score

        for child in node.children.all():
            next_state = dfa.transition(current_state, child.char)
            if next_state != -1:
                SearchByRegex._traverse_with_dfa(child, dfa, current_word, results, current_state)


class SearchWithRanking(APIView):
    def get(self, request, keyword, ranking, format=None):
        keyword = keyword.lower()
        valid_sort_options = ['occurrences', 'closeness', 'betweenness', 'pagerank']
        if ranking not in valid_sort_options:
            return Response({'error': f"Critère de tri invalide. Options valides : {valid_sort_options}"}, status=400)

        # Rechercher tous les mots commençant par le préfixe dans TrieNode
        prefix_results = TrieNode.search_by_prefix(keyword)
        if not prefix_results:
            return Response({'results': []})

        # Agréger les résultats par livre
        aggregated_results = defaultdict(lambda: {'score': 0.0, 'occurrences': 0})
        for result in prefix_results:
            word_data = result['data']
            for book_id, data in word_data.items():
                aggregated_results[book_id]['score'] += data['score']
                aggregated_results[book_id]['occurrences'] += data['occurrences']

        results = []
        for book_id in aggregated_results:
            try:
                book = BookText.objects.get(gutenberg_id=book_id)
                results.append({
                    'id': book.gutenberg_id,
                    'title': book.title,
                    'authors': book.authors,
                    'language': book.language,
                    'cover_url': f'https://gutenberg.org/files/{book.gutenberg_id}/{book.gutenberg_id}-h/images/cover.jpg',
                    'score': aggregated_results[book_id]['score'],
                    'occurrences': aggregated_results[book_id]['occurrences'],
                    'closeness': book.closeness_centrality,
                    'betweenness': book.betweenness_centrality,
                    'pagerank': book.pagerank
                })
            except BookText.DoesNotExist:
                continue

        if not results:
            return Response({'results': []})

        # Trier selon le critère choisi
        if ranking == 'occurrences':
            results = sorted(results, key=lambda x: x['occurrences'], reverse=True)
        elif ranking == 'closeness':
            results = sorted(results, key=lambda x: x['closeness'], reverse=True)
        elif ranking == 'betweenness':
            results = sorted(results, key=lambda x: x['betweenness'], reverse=True)
        elif ranking == 'pagerank':
            results = sorted(results, key=lambda x: x['pagerank'], reverse=True)

        return Response({'results': results})

class SearchWithSuggestions(APIView):
    def get(self, request, keyword, format=None):
        keyword = keyword.lower()
        # Rechercher tous les mots commençant par le préfixe dans TrieNode
        prefix_results = TrieNode.search_by_prefix(keyword)
        if not prefix_results:
            return Response({'results': [], 'suggestions': []})

        # Agréger les résultats par livre
        aggregated_results = defaultdict(lambda: {'score': 0.0, 'occurrences': 0})
        for result in prefix_results:
            word_data = result['data']
            for book_id, data in word_data.items():
                aggregated_results[book_id]['score'] += data['score']
                aggregated_results[book_id]['occurrences'] += data['occurrences']

        results = []
        for book_id in aggregated_results:
            try:
                book = BookText.objects.get(gutenberg_id=book_id)
                results.append({
                    'id': book.gutenberg_id,
                    'title': book.title,
                    'authors': book.authors,
                    'language': book.language,
                    'cover_url': f'https://gutenberg.org/files/{book.gutenberg_id}/{book.gutenberg_id}-h/images/cover.jpg',
                    'score': aggregated_results[book_id]['score'],
                    'occurrences': aggregated_results[book_id]['occurrences']
                })
            except BookText.DoesNotExist:
                continue

        # Trier les résultats par score décroissant
        results = sorted(results, key=lambda x: x['score'], reverse=True)

        # Sélectionner les 3 premiers livres pour les suggestions
        top_books = [result['id'] for result in results[:min(3, len(results))]]
        if not top_books:
            return Response({'results': [], 'suggestions': []})

        # Récupérer les suggestions depuis TableJaccard
        suggestions = {}
        for book_id in top_books:
            book = BookText.objects.get(gutenberg_id=book_id)
            neighbors = TableJaccard.objects.filter(
                models.Q(book1=book) | models.Q(book2=book)
            ).select_related('book1', 'book2')
            for sim in neighbors:
                neighbor = sim.book2 if sim.book1 == book else sim.book1
                if neighbor.gutenberg_id not in top_books and neighbor.gutenberg_id not in suggestions:
                    suggestions[neighbor.gutenberg_id] = {
                        'id': neighbor.gutenberg_id,
                        'title': neighbor.title,
                        'authors': neighbor.authors,
                        'language': neighbor.language,
                        'cover_url': f'https://gutenberg.org/files/{neighbor.gutenberg_id}/{neighbor.gutenberg_id}-h/images/cover.jpg',
                    }

        suggestion_list = list(suggestions.values())
        return Response({'results': results, 'suggestions': suggestion_list})