from django.db import models
import json
import zlib

class BookText(models.Model):
    gutenberg_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=500, blank=True)
    authors = models.JSONField(default=list, blank=True)
    word_count = models.IntegerField(default=0)
    language = models.CharField(max_length=2, choices=[('en', 'English'), ('fr', 'French')], default='en')

    closeness_centrality = models.FloatField(default=0.0)
    betweenness_centrality = models.FloatField(default=0.0)
    pagerank = models.FloatField(default=0.0)

    class Meta:
        ordering = ('gutenberg_id',)

class TableIndex(models.Model):
    word = models.CharField(max_length=50, unique=True)
    index_data = models.BinaryField(blank=True)

    # Décompression et désérialisation
    def get_index_data(self):
        if self.index_data:
            decompressed = zlib.decompress(self.index_data).decode('utf-8')
            return json.loads(decompressed)
        return {}

    # Sérialisation et compression
    def set_index_data(self, data):
        json_str = json.dumps(data)
        compressed = zlib.compress(json_str.encode('utf-8'))
        self.index_data = compressed

class TableJaccard(models.Model):
    book1 = models.ForeignKey(BookText, on_delete=models.CASCADE, related_name='similarities_as_book1')
    book2 = models.ForeignKey(BookText, on_delete=models.CASCADE, related_name='similarities_as_book2')
    jaccard_similarity = models.DecimalField(max_digits=5, decimal_places=4)

    class Meta:
        unique_together = ('book1', 'book2')
        indexes = [
            models.Index(fields=['book1', 'book2']),
        ]

    def __str__(self):
        return f"{self.book1.gutenberg_id} - {self.book2.gutenberg_id}: {self.jaccard_similarity}"
