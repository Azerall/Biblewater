from rest_framework.serializers import ModelSerializer
from mytig.models import ProduitEnPromotion, ProduitDisponible, ProduitImage
from myImageBank.models import ImageEntry

class ProduitEnPromotionSerializer(ModelSerializer):
    class Meta:
        model = ProduitEnPromotion
        fields = ('id', 'tigID')

class ProduitDisponibleSerializer(ModelSerializer):
    class Meta:
        model = ProduitDisponible
        fields = ('id', 'tigID')

class ProduitImageSerializer(ModelSerializer):
    class Meta:
        model = ProduitImage
        fields = ('id', 'tigID', 'image')