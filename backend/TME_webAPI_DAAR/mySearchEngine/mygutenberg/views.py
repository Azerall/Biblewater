import requests
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from django.db import models
from mygutenberg.models import BookText, TableIndex, TableJaccard
from mygutenberg.algorithms.centrality import build_graph, closeness_centrality, betweenness_centrality, pagerank

# URL de base pour l'API Gutendex
base_url = 'https://gutendex.com/books/'

class BooksList(APIView):
    def get(self, request, format=None):
        books = BookText.objects.all()
        return Response([{
            'id': book.gutenberg_id,
            'title': book.title,
            'authors': book.authors,
            'language': book.language
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
                'content': content
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
            'language': book.language
        } for book in books])

class EnglishBooksList(APIView):
    def get(self, request, format=None):
        books = BookText.objects.filter(language='en')
        return Response([{
            'id': book.gutenberg_id,
            'title': book.title,
            'authors': book.authors,
            'language': book.language
        } for book in books])

class BookCoverImage(APIView):
    def get(self, request, book_id, format=None):
        try:
            book = BookText.objects.get(gutenberg_id=book_id)
            gutendex_url = f'https://gutendex.com/books/{book_id}/'
            response = requests.get(gutendex_url)
            response.raise_for_status()
            book_data = response.json()
            formats = book_data.get('formats', {})
            cover_url = formats.get('image/jpeg', None)
            if not cover_url:
                cover_url = f'https://gutenberg.org/files/{book_id}/{book_id}-h/images/cover.jpg'
                try:
                    requests.head(cover_url).raise_for_status()
                except requests.RequestException:
                    cover_url = None  # Pas de couverture trouvée
            return Response({'id': book_id, 'cover_image': cover_url})
        except BookText.DoesNotExist:
            raise Http404
        except requests.RequestException:
            return Response({'error': 'Unable to fetch cover image'}, status=500)

class SearchByKeyword(APIView):
    def get(self, request, keyword, format=None):
        keyword = keyword.lower()
        try:
            index = TableIndex.objects.get(word=keyword)
            index_data = index.get_index_data()  # {book_id: {occurrences, tfidf, score}}
            results = []
            for book_id, data in index_data.items():
                book = BookText.objects.get(gutenberg_id=book_id)
                results.append({
                    'id': book.gutenberg_id,
                    'title': book.title,
                    'authors': book.authors,
                    'language': book.language,
                    'score': data['score'],
                    'occurrences': data['occurrences']
                })
            # Trier les résultats par score décroissant
            results = sorted(results, key=lambda x: x['score'], reverse=True)
            return Response(results)
        except TableIndex.DoesNotExist:
            return Response([])  # Aucun mot trouvé dans l’index

class SearchByRegex(APIView):
    def get(self, request, regex, format=None):
        try:
            pattern = re.compile(regex)
            results = {}
            indices = TableIndex.objects.all()

            for index in indices:
                word = index.word
                if pattern.search(word):
                    index_data = index.get_index_data()  # {book_id: {occurrences, tfidf, score}}
                    for book_id, data in index_data.items():
                        if book_id not in results:
                            book = BookText.objects.get(gutenberg_id=book_id)
                            results[book_id] = {
                                'id': book.gutenberg_id,
                                'title': book.title,
                                'authors': book.authors,
                                'language': book.language,
                                'score': 0,
                                'matches': 0
                            }
                        results[book_id]['score'] += data['score']
                        results[book_id]['matches'] += 1

            # Convertir en liste et trier par score
            results = list(results.values())
            results = sorted(results, key=lambda x: x['score'], reverse=True)
            return Response(results)
        except re.error:
            raise Http404("Invalid regex")

class SearchWithRanking(APIView):
    def get(self, request, keyword, sort_by, format=None):
        keyword = keyword.lower()
        valid_sort_options = ['occurrences', 'closeness', 'betweenness', 'pagerank']
        if sort_by not in valid_sort_options:
            return Response({'error': f"Critère de tri invalide. Options valides : {valid_sort_options}"}, status=400)

        try:
            # Récupérer les résultats de recherche
            index = TableIndex.objects.get(word=keyword)
            index_data = index.get_index_data()
            results = []
            for book_id, data in index_data.items():
                book = BookText.objects.get(gutenberg_id=book_id)
                results.append({
                    'id': book.gutenberg_id,
                    'title': book.title,
                    'authors': book.authors,
                    'language': book.language,
                    'score': data['score'],
                    'occurrences': data['occurrences'],
                    'closeness': book.closeness_centrality,
                    'betweenness': book.betweenness_centrality,
                    'pagerank': book.pagerank
                })

            if not results:
                return Response({'results': []})

            # Trier selon le critère choisi
            if sort_by == 'occurrences':
                results = sorted(results, key=lambda x: x['occurrences'], reverse=True)
            elif sort_by == 'closeness':
                results = sorted(results, key=lambda x: x['closeness'], reverse=True)
            elif sort_by == 'betweenness':
                results = sorted(results, key=lambda x: x['betweenness'], reverse=True)
            elif sort_by == 'pagerank':
                results = sorted(results, key=lambda x: x['pagerank'], reverse=True)

            return Response({'results': results})
        except TableIndex.DoesNotExist:
            return Response({'results': []})

class SearchWithSuggestions(APIView):
    def get(self, request, keyword, format=None):
        keyword = keyword.lower()
        try:
            index = TableIndex.objects.get(word=keyword)
            index_data = index.get_index_data()  # {book_id: {occurrences, tfidf, score}}
            results = []
            for book_id, data in index_data.items():
                book = BookText.objects.get(gutenberg_id=book_id)
                results.append({
                    'id': book.gutenberg_id,
                    'title': book.title,
                    'authors': book.authors,
                    'language': book.language,
                    'score': data['score'],
                    'occurrences': data['occurrences']
                })
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
                            'language': neighbor.language
                        }

            suggestion_list = list(suggestions.values())
            return Response({'results': results, 'suggestions': suggestion_list})
        except TableIndex.DoesNotExist:
            return Response({'results': [], 'suggestions': []})