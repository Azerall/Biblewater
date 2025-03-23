from django.core.management.base import BaseCommand
from collections import defaultdict
from mygutenberg.models import BookText, TableJaccard
from django.db import models

class Command(BaseCommand):
    help = 'Remplit et indexe les livres Gutenberg, construit le Trie, et calcule les similarités Jaccard.'

    def handle(self, *args, **options):
        # Récupérer toutes les entrées de TableJaccard
        table_jaccard = TableJaccard.objects.all()
        graph = build_graph(table_jaccard)

        # Livres cibles
        target_books = [
            (128, "The Arabian Nights Entertainments"),
            (12545, "Traditions of the Tinguian: A Study in Philippine Folk-Lore")
        ]

        # Afficher les voisins pour chaque livre cible
        for book_id, book_title in target_books:
            print(f"\nVoisins de '{book_title}' (gutenberg_id={book_id}):")
            neighbors = get_neighbors(book_id, graph, table_jaccard)
            
            if neighbors:
                for neighbor in sorted(neighbors, key=lambda x: x['jaccard_similarity'], reverse=True):
                    print(f"- {neighbor['gutenberg_id']}: {neighbor['title']} (Jaccard: {neighbor['jaccard_similarity']})")
            else:
                print("Aucun voisin trouvé.")

def build_graph(table_jaccard):
    graph = defaultdict(set)
    for sim in table_jaccard:
        book1_id = sim.book1.gutenberg_id
        book2_id = sim.book2.gutenberg_id
        graph[book1_id].add(book2_id)
        graph[book2_id].add(book1_id)  # Graphe non dirigé
    return graph

def get_neighbors(book_id, graph, table_jaccard):
    """Récupère les voisins d'un livre avec leurs titres et scores Jaccard."""
    neighbors = graph[book_id]
    neighbor_details = []
    
    # Pour chaque voisin, trouve le score Jaccard dans TableJaccard
    for neighbor_id in neighbors:
        # Requête pour obtenir la similarité (book1 ou book2 peut être le livre cible)
        try:
            sim = table_jaccard.filter(
                models.Q(book1__gutenberg_id=book_id, book2__gutenberg_id=neighbor_id) |
                models.Q(book1__gutenberg_id=neighbor_id, book2__gutenberg_id=book_id)
            ).first()
            jaccard_score = float(sim.jaccard_similarity) if sim else 0.0
            neighbor_book = BookText.objects.get(gutenberg_id=neighbor_id)
            neighbor_details.append({
                'gutenberg_id': neighbor_id,
                'title': neighbor_book.title,
                'jaccard_similarity': jaccard_score
            })
        except BookText.DoesNotExist:
            print(f"Livre {neighbor_id} non trouvé dans BookText.")
    
    return neighbor_details
