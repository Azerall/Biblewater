from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
import secrets
import requests
from myImageBank.models import ImageEntry
from myImageBank.serializers import ImageEntrySerializer
from mytig.models import ProduitImage
from mytig.config import baseUrl

class RandomImage(APIView):
    def get(self, request, format=None):
        try:
            random_image = secrets.choice(ImageEntry.objects.all())
            serializer = ImageEntrySerializer(random_image)
            return Response({'url': serializer.data['url']})
        except IndexError:
            raise Http404

class Image(APIView):
    def get(self, request, image_id, format=None):
        try:
            image = ImageEntry.objects.get(id=image_id)
            serializer = ImageEntrySerializer(image)
            return Response({'url': serializer.data['url']})
        except ImageEntry.DoesNotExist:
            raise Http404

class ImageFromString(APIView):
    def get(self, request, newName, format=None):
        try:
            # Trouver un produit avec ce nom dans ProduitImage
            produit_image = ProduitImage.objects.filter(tigID__in=[
                p['id'] for p in requests.get(baseUrl + 'products/').json()
                if p['name'] == newName
            ]).first()
            if not produit_image:
                raise Http404(f"Aucune image associée au nom '{newName}'")
            serializer = ImageEntrySerializer(produit_image.image)
            return Response({'url': serializer.data['url']})
        except ProduitImage.DoesNotExist:
            raise Http404(f"Aucune image associée au nom '{newName}'")