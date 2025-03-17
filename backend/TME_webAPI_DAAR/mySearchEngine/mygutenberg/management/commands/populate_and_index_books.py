from django.core.management.base import BaseCommand
import requests
import time
import re
import json
from collections import defaultdict
from mygutenberg.models import BookText, TableIndex
from mygutenberg.algorithms.tfidf import index_document

class Command(BaseCommand):
    help = 'Populate and index Gutenberg books.'

    def handle(self, *args, **options):
        self.stdout.write(f"[{time.ctime()}] Populating and indexing books...")

        # Configuration
        base_url = 'https://gutendex.com/books/'
        target_count = 1664  # 1664 pour le projet final
        page = 1
        books_added = 0

        whitelists = {
            'en': 'words_alpha.txt',
            'fr': 'liste.de.mots.francais.frgut.txt'
        }
        languages = ['en', 'fr']
        all_docs = {}
        book_meta = {}

        # Load whitelists
        whitelist_data = {}
        for lang in languages:
            with open(whitelists[lang], 'r') as f:
                whitelist_data[lang] = set(line.strip().lower() for line in f if len(line.strip()) > 2)
            self.stdout.write(f"[{time.ctime()}] {len(whitelist_data[lang])} words loaded for {lang}.")

        # Fetch and process books
        while books_added < target_count:
            self.stdout.write(f"[{time.ctime()}] Fetching page {page}...")
            response = requests.get(f'{base_url}?page={page}&languages=fr,en')
            books = response.json().get('results', [])
            self.stdout.write(f"[{time.ctime()}] Found {len(books)} books.")

            for book in books:
                book_id = book['id']
                if BookText.objects.filter(gutenberg_id=book_id).exists():
                    self.stdout.write(f"[{time.ctime()}] Skipping book {book_id} (already exists)")
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

                    if len(filtered_words) >= 10000 and len(filtered_words) <= 100000:
                        title = book.get('title', 'Unknown')
                        authors_list = [{'name': a.get('name', '')} for a in book.get('authors', [])]

                        all_docs[book_id] = filtered_words
                        book_meta[book_id] = {'title': title, 'authors': authors_list, 'language': language}

                        BookText.objects.create(
                            gutenberg_id=book_id,
                            title=title,
                            authors=authors_list,
                            word_count=len(filtered_words),
                            language=language
                        )

                        books_added += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"[{time.ctime()}] Added book {book_id} ({len(filtered_words)} words, {language}) - {books_added}/{target_count}"
                        ))

                        if books_added >= target_count:
                            break

                except requests.RequestException as e:
                    self.stdout.write(self.style.WARNING(f"[{time.ctime()}] Failed to fetch book {book_id}: {str(e)}"))
                    continue

            self.stdout.write(f"[{time.ctime()}] Page {page} completed - Total books added: {books_added}/{target_count}")
            page += 1

        self.stdout.write(f"[{time.ctime()}] Finished fetching. Total books added: {books_added}")

        # Pre-calculate Document Frequencies (DF)
        self.stdout.write(f"[{time.ctime()}] Calculating Document Frequencies (DF)...")
        document_frequencies = defaultdict(int)
        for words in all_docs.values():
            for term in set(words):
                document_frequencies[term] += 1
        total_documents = len(all_docs)
        self.stdout.write(f"[{time.ctime()}] DF calculated for {len(document_frequencies)} unique terms across {total_documents} documents.")

        # Indexing step using tfidf
        self.stdout.write(f"[{time.ctime()}] Starting indexing for {total_documents} books...")
        index = defaultdict(dict)  # term -> { book_id: {data} }
        books_processed = 0
        total_words_indexed = 0

        for book_id, filtered_words in all_docs.items():
            books_processed += 1
            self.stdout.write(f"[{time.ctime()}] Indexing book {book_id} ({books_processed}/{total_documents})...")

            meta = book_meta[book_id]
            title_words = re.split(r'[^A-Za-z]+', meta['title'].lower())
            author_words = []
            for author in meta['authors']:
                author_words.extend(re.split(r'[^A-Za-z]+', author['name'].lower()))

            doc_index = index_document(
                document_words=filtered_words,
                total_documents=total_documents,
                document_frequencies=document_frequencies,
                title_words=title_words,
                author_words=author_words
            )

            for word, data in doc_index.items():
                index[word][book_id] = data
                total_words_indexed += 1

        self.stdout.write(f"[{time.ctime()}] Index built with {len(index)} unique words and {total_words_indexed} total entries.")

        # Save index
        self.stdout.write(f"[{time.ctime()}] Saving index with {len(index)} entries...")
        index_entries = [
            TableIndex(word=word, index_data=json.dumps(index_data))
            for word, index_data in index.items()
        ]
        TableIndex.objects.bulk_create(index_entries, batch_size=500, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"[{time.ctime()}] Successfully added and indexed {books_added} books!"))