from django.core.management.base import BaseCommand
import time
import re
import math
from mygutenberg.models import BookText

class Command(BaseCommand):
    help = 'Manually index Gutenberg books with TF-IDF.'

    def handle(self, *args, **options):
        self.stdout.write('[' + time.ctime() + '] Indexing books...')
        books = BookText.objects.all()
        if not books:
            self.stdout.write(self.style.ERROR('No books in database. Run populate_books first.'))
            return

        # Charger la whitelist
        with open('words_alpha.txt', 'r') as f:
            whitelist = set(line.strip().lower() for line in f if len(line.strip()) > 2)

        # Étape 1 : Construire un index par livre et compter les occurrences
        book_indices = []
        doc_freq = {}  # Nombre de documents contenant chaque mot
        for book in books:
            words = re.split(r'[^A-Za-z]+', book.content.lower())
            filtered_words = [w for w in words if w in whitelist and len(w) > 2]
            word_count = len(filtered_words)
            book.word_count = word_count
            book.save()

            index = {}
            for word in filtered_words:
                index[word] = index.get(word, 0) + 1
                doc_freq[word] = doc_freq.get(word, 0) + (1 if index[word] == 1 else 0)
            book_indices.append((book, index))

        # Étape 2 : Calculer TF-IDF et scores
        total_docs = len(books)
        for book, index in book_indices:
            indexed_data = {}
            for word, occurrences in index.items():
                # TF = occurrences / total mots dans le livre
                tf = occurrences / book.word_count
                # IDF = log(N / nombre de docs avec le mot)
                idf = math.log(total_docs / (doc_freq[word] + 1))  # +1 pour éviter division par 0
                tfidf = tf * idf
                # Score ajusté avec poids
                score = tfidf
                if word in book.title.lower():
                    score *= 5  # Poids titre
                if book.author and word in book.author.lower():
                    score *= 10  # Poids auteur
                indexed_data[word] = {'occurrences': occurrences, 'tfidf': tfidf, 'score': score}
            book.index_table = json.dumps(indexed_data)
            book.save()
            self.stdout.write(self.style.SUCCESS(
                f'[{time.ctime()}] Indexed book {book.gutenberg_id} ({book.title})'
            ))

        self.stdout.write('[' + time.ctime() + '] Indexing completed.')