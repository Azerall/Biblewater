import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404, JsonResponse
from mygutenberg.models import LivreEnFrancais, LivreEnAnglais, BookText
from mygutenberg.serializers import LivreEnFrancaisSerializer, LivreEnAnglaisSerializer
import secrets
from myImageBank.models import ImageEntry

# URL de base pour l'API Gutendex
base_url = 'https://gutendex.com/books/'

# Liste complète des livres
class BooksList(APIView):
    def get(self, request, format=None):
        response = requests.get(base_url)
        jsondata = response.json()
        return Response(jsondata['results'])  # Renvoie uniquement la liste des livres

# Détails d'un livre spécifique
class BookDetail(APIView):
    def get(self, request, pk, format=None):
        try:
            response = requests.get(base_url + str(pk) + '/')
            jsondata = response.json()
            return Response(jsondata)
        except requests.exceptions.RequestException:
            raise Http404

# Liste des livres en français
class FrenchBooksList(APIView):
    def get(self, request, format=None):
        res = []
        for book in LivreEnFrancais.objects.all():
            serializer = LivreEnFrancaisSerializer(book)
            response = requests.get(base_url + str(serializer.data['gutenbergID']) + '/')
            jsondata = response.json()
            res.append(jsondata)
        return JsonResponse(res, safe=False)

# Détails d'un livre en français
class FrenchBookDetail(APIView):
    def get_object(self, pk):
        try:
            return LivreEnFrancais.objects.get(pk=pk)
        except LivreEnFrancais.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        book = self.get_object(pk)
        serializer = LivreEnFrancaisSerializer(book)
        response = requests.get(base_url + str(serializer.data['gutenbergID']) + '/')
        jsondata = response.json()
        return Response(jsondata)

# Liste des livres en anglais
class EnglishBooksList(APIView):
    def get(self, request, format=None):
        res = []
        for book in LivreEnAnglais.objects.all():
            serializer = LivreEnAnglaisSerializer(book)
            response = requests.get(base_url + str(serializer.data['gutenbergID']) + '/')
            jsondata = response.json()
            res.append(jsondata)
        return JsonResponse(res, safe=False)

# Détails d'un livre en anglais
class EnglishBookDetail(APIView):
    def get_object(self, pk):
        try:
            return LivreEnAnglais.objects.get(pk=pk)
        except LivreEnAnglais.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        book = self.get_object(pk)
        serializer = LivreEnAnglaisSerializer(book)
        response = requests.get(base_url + str(serializer.data['gutenbergID']) + '/')
        jsondata = response.json()
        return Response(jsondata)

# Nouvelles vues pour l'Exercice 10
class BookCoverImage(APIView):
    def get(self, request, book_id, format=None):
        try:
            # Chercher une image de couverture (hypothèse : contient 'cover' dans l'URL)
            cover_image = ImageEntry.objects.filter(
                book_id=book_id,
                url__contains='cover'
            ).first()
            if not cover_image:
                raise Http404(f"Aucune image de couverture pour le livre {book_id}")
            return Response({'url': cover_image.url})
        except ImageEntry.DoesNotExist:
            raise Http404(f"Aucune image de couverture pour le livre {book_id}")

class BookRandomImage(APIView):
    def get(self, request, book_id, format=None):
        try:
            images = ImageEntry.objects.filter(book_id=book_id)
            if not images.exists():
                raise Http404(f"Aucune image pour le livre {book_id}")
            random_image = secrets.choice(images)
            return Response({'url': random_image.url})
        except IndexError:
            raise Http404(f"Aucune image pour le livre {book_id}")

class BookSpecificImage(APIView):
    def get(self, request, book_id, image_id, format=None):
        try:
            image = ImageEntry.objects.get(book_id=book_id, id=image_id)
            return Response({'url': image.url})
        except ImageEntry.DoesNotExist:
            raise Http404(f"Image {image_id} non trouvée pour le livre {book_id}")
        
class SearchByKeyword(APIView):
    def get(self, request, keyword, format=None):
        keyword = keyword.lower()
        books = BookText.objects.all()
        results = []
        for book in books:
            index = book.get_index()
            if keyword in index:
                results.append({
                    'id': book.gutenberg_id,
                    'title': book.title,
                    'author': book.author,
                    'score': index[keyword]['score'],
                    'occurrences': index[keyword]['occurrences']
                })
            elif kmp_search(book.content.lower(), keyword) != -1:
                occurrences = book.content.lower().count(keyword)
                score = occurrences / book.word_count  # TF simple
                results.append({
                    'id': book.gutenberg_id,
                    'title': book.title,
                    'author': book.author,
                    'score': score,
                    'occurrences': occurrences
                })
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        return Response(results)

class SearchByRegex(APIView):
    def get(self, request, regex, format=None):
        try:
            pattern = re.compile(regex)
            books = BookText.objects.all()
            results = []
            for book in books:
                index = book.get_index()
                matches = [w for w in index.keys() if pattern.search(w)]
                if matches:
                    score = sum(index[w]['score'] for w in matches)
                    results.append({
                        'id': book.gutenberg_id,
                        'title': book.title,
                        'author': book.author,
                        'score': score,
                        'matches': len(matches)
                    })
                else:
                    content_matches = pattern.findall(book.content)
                    if content_matches:
                        score = len(content_matches) / book.word_count
                        results.append({
                            'id': book.gutenberg_id,
                            'title': book.title,
                            'author': book.author,
                            'score': score,
                            'matches': len(content_matches)
                        })
            results = sorted(results, key=lambda x: x['score'], reverse=True)
            return Response(results)
        except re.error:
            raise Http404("Expression régulière invalide")

class SearchWithSuggestions(APIView):
    def manual_jaccard(self, set1, set2):
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0

    def build_graph(self, books):
        graph = {}  # Dictionnaire d'adjacence
        for i, book1 in enumerate(books):
            index1 = set(book1.get_index().keys())
            graph[book1.gutenberg_id] = []
            for book2 in books[i+1:]:
                index2 = set(book2.get_index().keys())
                if self.manual_jaccard(index1, index2) > 0.1:  # Seuil
                    graph[book1.gutenberg_id].append(book2.gutenberg_id)
                    if book2.gutenberg_id not in graph:
                        graph[book2.gutenberg_id] = []
                    graph[book2.gutenberg_id].append(book1.gutenberg_id)
        return graph

    def manual_pagerank(self, graph, damping=0.85, iterations=100):
        N = len(graph)
        if N == 0:
            return {}
        pr = {node: 1/N for node in graph}
        for _ in range(iterations):
            new_pr = {}
            for node in graph:
                rank_sum = sum(pr[neighbor] / len(graph[neighbor]) for neighbor in graph[node])
                new_pr[node] = (1 - damping) / N + damping * rank_sum
            pr = new_pr
        return pr

    def get(self, request, keyword, format=None):
        keyword = keyword.lower()
        books = list(BookText.objects.all())
        results = []
        for book in books:
            index = book.get_index()
            if keyword in index:
                results.append({
                    'id': book.gutenberg_id,
                    'title': book.title,
                    'author': book.author,
                    'score': index[keyword]['score'],
                    'occurrences': index[keyword]['occurrences']
                })

        results = sorted(results, key=lambda x: x['score'], reverse=True)
        if not results:
            return Response({'results': [], 'suggestions': []})

        # Construire un graphe de similarité
        graph = self.build_graph(books)
        pagerank = self.manual_pagerank(graph)

        # Ajouter PageRank aux résultats
        for res in results:
            res['pagerank'] = pagerank.get(res['id'], 0)
        results = sorted(results, key=lambda x: x['pagerank'], reverse=True)

        # Suggestions : voisins des top 3
        top_ids = [r['id'] for r in results[:3]]
        suggestions = []
        seen = set(top_ids)
        for book in books:
            if book.gutenberg_id not in seen and book.gutenberg_id in graph:
                if any(neighbor in top_ids for neighbor in graph[book.gutenberg_id]):
                    suggestions.append({
                        'id': book.gutenberg_id,
                        'title': book.title,
                        'author': book.author
                    })
                    seen.add(book.gutenberg_id)

        return Response({'results': results[:10], 'suggestions': suggestions[:5]})