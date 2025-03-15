import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import renderers
from django.http import Http404
from django.http import JsonResponse
from mytig.config import baseUrl
import secrets

from mytig.models import ProduitEnPromotion, ProduitDisponible, ProduitImage
from mytig.serializers import ProduitEnPromotionSerializer, ProduitDisponibleSerializer

class RedirectionListeDeProduits(APIView):
    def get(self, request, format=None):
        response = requests.get(baseUrl + 'products/')
        jsondata = response.json()
        return Response(jsondata)

class RedirectionDetailProduit(APIView):
    def get(self, request, pk, format=None):
        try:
            response = requests.get(baseUrl + 'product/' + str(pk) + '/')
            jsondata = response.json()
            return Response(jsondata)
        except:
            raise Http404

class JPEGRenderer(renderers.BaseRenderer):
    media_type = 'image/jpeg'
    format = 'jpg'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data

class ProduitImageRandom(APIView):
    renderer_classes = [JPEGRenderer]
    def get(self, request, pk, format=None):
        try:
            images = ProduitImage.objects.filter(tigID=pk)
            if not images.exists():
                raise Http404("Aucune image associée à ce produit")
            random_image = secrets.choice(images)
            image_url = random_image.image.url
            image_response = requests.get(image_url, stream=True)
            return Response(image_response.content)
        except:
            raise Http404

class ProduitImageView(APIView):
    renderer_classes = [JPEGRenderer, renderers.JSONRenderer]
    def get(self, request, pk, image_id, format=None):
        try:
            produit_image = ProduitImage.objects.get(tigID=pk, image__id=image_id)
            image_url = produit_image.image.url
            image_response = requests.get(image_url, stream=True)
            return Response(image_response.content)
        except ProduitImage.DoesNotExist:
            raise Http404("Image non trouvée pour ce produit")

class PromoList(APIView):
    def get(self, request, format=None):
        res = []
        for prod in ProduitEnPromotion.objects.all():
            serializer = ProduitEnPromotionSerializer(prod)
            response = requests.get(baseUrl + 'product/' + str(serializer.data['tigID']) + '/')
            jsondata = response.json()
            res.append(jsondata)
        return JsonResponse(res, safe=False)

class PromoDetail(APIView):
    def get_object(self, pk):
        try:
            return ProduitEnPromotion.objects.get(pk=pk)
        except ProduitEnPromotion.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        prod = self.get_object(pk)
        serializer = ProduitEnPromotionSerializer(prod)
        response = requests.get(baseUrl + 'product/' + str(serializer.data['tigID']) + '/')
        jsondata = response.json()
        return Response(jsondata)

class RedirectionListeDeShipPoints(APIView):
    def get(self, request, format=None):
        response = requests.get(baseUrl + 'shipPoints/')
        jsondata = response.json()
        return Response(jsondata)

class RedirectionDetailShipPoint(APIView):
    def get(self, request, pk, format=None):
        try:
            response = requests.get(baseUrl + 'shipPoint/' + str(pk) + '/')
            jsondata = response.json()
            return Response(jsondata)
        except:
            raise Http404

class AvailableList(APIView):
    def get(self, request, format=None):
        res = []
        for prod in ProduitDisponible.objects.all():
            serializer = ProduitDisponibleSerializer(prod)
            response = requests.get(baseUrl + 'product/' + str(serializer.data['tigID']) + '/')
            jsondata = response.json()
            res.append(jsondata)
        return JsonResponse(res, safe=False)

class AvailableDetail(APIView):
    def get_object(self, pk):
        try:
            return ProduitDisponible.objects.get(pk=pk)
        except ProduitDisponible.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        prod = self.get_object(pk)
        serializer = ProduitDisponibleSerializer(prod)
        response = requests.get(baseUrl + 'product/' + str(serializer.data['tigID']) + '/')
        jsondata = response.json()
        return Response(jsondata)