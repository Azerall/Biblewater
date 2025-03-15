from django.core.management.base import BaseCommand
import requests
import time
from myImageBank.models import ImageEntry
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'Refresh the image index with Gutenberg book images.'

    def handle(self, *args, **options):
        self.stdout.write('[' + time.ctime() + '] Refreshing Gutenberg images...')
        book_ids = [56667]  # Liste d'IDs à indexer (à étendre selon besoin)

        for book_id in book_ids:
            base_url = f'http://gutenberg.org/files/{book_id}/{book_id}-h/images/'
            try:
                response = requests.get(base_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # Trouver toutes les images (liens vers .jpg, .png, etc.)
                image_links = soup.find_all('a', href=True)
                for link in image_links:
                    href = link['href']
                    if href.endswith(('.jpg', '.png', '.gif')):
                        image_url = base_url + href
                        # Ajouter ou mettre à jour dans ImageEntry
                        ImageEntry.objects.get_or_create(
                            url=image_url,
                            defaults={'book_id': book_id}
                        )
                        self.stdout.write(self.style.SUCCESS(
                            f'[{time.ctime()}] Indexed image {image_url} for book {book_id}'
                        ))

            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(
                    f'[{time.ctime()}] Error fetching images for book {book_id}: {str(e)}'
                ))

        self.stdout.write('[' + time.ctime() + '] Gutenberg images refresh terminated.')