from django.core.management.base import BaseCommand
from mytig.models import ProduitImage
from myImageBank.models import ImageEntry
from mytig.config import baseUrl
import requests
import time
import secrets

class Command(BaseCommand):
    help = 'Refresh the association of images to products based on their names.'

    def handle(self, *args, **options):
        self.stdout.write('[' + time.ctime() + '] Refreshing image associations...')
        response = requests.get(baseUrl + 'products/')
        jsondata = response.json()

        available_images = list(ImageEntry.objects.all())
        if not available_images:
            self.stdout.write(self.style.ERROR('[' + time.ctime() + '] No images available in ImageEntry'))
            return

        # Ne supprimer que les tigID absents de l'API distante
        current_ids = {product['id'] for product in jsondata}
        ProduitImage.objects.exclude(tigID__in=current_ids).delete()

        # Ajouter ou mettre à jour les associations
        for product in jsondata:
            if 'id' in product:
                tig_id = product['id']
                if not ProduitImage.objects.filter(tigID=tig_id).exists():
                    random_image = secrets.choice(available_images)
                    ProduitImage.objects.create(
                        tigID=tig_id,
                        image=random_image
                    )
                    self.stdout.write(self.style.SUCCESS(
                        '[' + time.ctime() + '] Associated image to product id="%s" (name="%s")' % (tig_id, product.get('name', 'Unknown'))
                    ))

        self.stdout.write('[' + time.ctime() + '] Image associations refresh terminated.')