from django.db import models

class ImageEntry(models.Model):
    url = models.URLField(max_length=500)
    book_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('id',)