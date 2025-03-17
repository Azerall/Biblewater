from django.core.management.base import BaseCommand
from mygutenberg.models import BookText, TableIndex, TableJaccard
from mygutenberg.algorithms.jaccard import compute_jaccard_similarity
from mygutenberg.algorithms.centrality import build_graph, closeness_centrality, betweenness_centrality, pagerank

class Command(BaseCommand):
    help = 'Remplit la table TableJaccard avec les similarités de Jaccard entre les livres'

    def handle(self, *args, **options):
        threshold = 0.41
        self.stdout.write(f"Calcul des similarités de Jaccard avec un seuil de {threshold}...")

        # Récupérer tous les livres et indices
        books = BookText.objects.all()
        book_ids = [book.gutenberg_id for book in books]
        table_indices = TableIndex.objects.all()

        if not book_ids or not table_indices:
            self.stdout.write(self.style.ERROR("Aucun livre ou index trouvé dans la base de données."))
            return

        # Calculer les similarités
        similarities = compute_jaccard_similarity(book_ids, table_indices)
        if similarities is None:
            self.stdout.write(self.style.ERROR("Erreur : compute_jaccard_similarity a retourné None"))
            return

        # Vider l'ancienne table
        TableJaccard.objects.all().delete()

        # Remplir la table
        created_count = 0
        for (id1, id2), similarity in similarities.items():
            if similarity >= threshold:
                self.stdout.write(f"Similarité trouvée entre {id1} et {id2}: {similarity}")
                try:
                    book1 = BookText.objects.get(gutenberg_id=id1)
                    book2 = BookText.objects.get(gutenberg_id=id2)
                    TableJaccard.objects.create(
                        book1=book1,
                        book2=book2,
                        jaccard_similarity=similarity
                    )
                    created_count += 1
                except BookText.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Livre {id1} ou {id2} non trouvé."))
                    continue

        self.stdout.write(self.style.SUCCESS(f"{created_count} similarités enregistrées avec succès."))

        # Afficher le nombre de livres sans similarité
        no_similarity_count = len(book_ids) - created_count
        self.stdout.write(f"{no_similarity_count} livres sans similarité.")

        # Construire le graphe et calculer les centralités
        graph = build_graph(TableJaccard.objects.all())
        if graph:
            # Calculer les centralités
            closeness = closeness_centrality(graph, book_ids)
            betweenness = betweenness_centrality(graph, book_ids)
            pagerank_scores = pagerank(graph, book_ids)

            # Mettre à jour les livres avec les centralités
            for book in books:
                book.closeness_centrality = closeness.get(book.gutenberg_id, 0.0)
                book.betweenness_centrality = betweenness.get(book.gutenberg_id, 0.0)
                book.pagerank = pagerank_scores.get(book.gutenberg_id, 0.0)
                book.save()

            self.stdout.write(self.style.SUCCESS("Centralités calculées et enregistrées dans BookText."))
        else:
            self.stdout.write(self.style.WARNING("Aucun graphe généré."))