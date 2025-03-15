from django.core.management.base import BaseCommand
import requests
import time
from mygutenberg.models import BookText
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'Populate the database with Gutenberg book texts.'

    def handle(self, *args, **options):
        self.stdout.write('[' + time.ctime() + '] Populating books...')
        base_url = 'https://gutendex.com/books/'
        target_count = 1664
        page = 1
        books_added = 0

        while books_added < target_count:
            response = requests.get(f'{base_url}?page={page}')
            jsondata = response.json()
            for book in jsondata['results']:
                book_id = book['id']
                if BookText.objects.filter(gutenberg_id=book_id).exists():
                    continue

                # Télécharger le texte brut
                text_url = f'http://gutenberg.org/ebooks/{book_id}.txt.utf-8'
                try:
                    text_response = requests.get(text_url)
                    text_response.raise_for_status()
                    content = text_response.text
                    word_count = len(content.split())
                    if word_count >= 10000:  # Filtrer les livres >= 10 000 mots
                        BookText.objects.create(
                            gutenberg_id=book_id,
                            title=book.get('title', 'Unknown'),
                            content=content,
                            word_count=word_count
                        )
                        books_added += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'[{time.ctime()}] Added book {book_id} ({word_count} words)'
                        ))
                        if books_added >= target_count:
                            break
                except requests.RequestException:
                    continue
            page += 1

        self.stdout.write(f'[{time.ctime()}] Added {books_added} books.')