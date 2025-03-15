from rest_framework.serializers import ModelSerializer
from myImageBank.models import ImageEntry

class ImageEntrySerializer(ModelSerializer):
    class Meta:
        model = ImageEntry
        fields = ('id', 'url')