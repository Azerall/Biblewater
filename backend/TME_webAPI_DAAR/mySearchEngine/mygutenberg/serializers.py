from rest_framework.serializers import ModelSerializer
from mygutenberg.models import LivreEnFrancais, LivreEnAnglais

class LivreEnFrancaisSerializer(ModelSerializer):
    class Meta:
        model = LivreEnFrancais
        fields = ('id', 'gutenbergID')

class LivreEnAnglaisSerializer(ModelSerializer):
    class Meta:
        model = LivreEnAnglais
        fields = ('id', 'gutenbergID')