from django.db import models
import json

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
    index_data = models.TextField(blank=True)  # JSON : {book_id: {occurrences, tfidf, score}}

    def get_index_data(self):
        return json.loads(self.index_data) if self.index_data else {}

class TableJaccard(models.Model):
    book1 = models.ForeignKey(BookText, on_delete=models.CASCADE, related_name='similarities_as_book1')
    book2 = models.ForeignKey(BookText, on_delete=models.CASCADE, related_name='similarities_as_book2')
    jaccard_similarity = models.FloatField()  # Score de similarité entre 0 et 1

    class Meta:
        unique_together = ('book1', 'book2')
        indexes = [
            models.Index(fields=['book1', 'book2']),
        ]

    def __str__(self):
        return f"{self.book1.gutenberg_id} - {self.book2.gutenberg_id}: {self.jaccard_similarity}"