from django.db import models
import json

class LivreEnFrancais(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    gutenbergID = models.IntegerField(default='-1')

    class Meta:
        ordering = ('gutenbergID',)

class LivreEnAnglais(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    gutenbergID = models.IntegerField(default='-1')

    class Meta:
        ordering = ('gutenbergID',)

class BookText(models.Model):
    gutenberg_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=500, blank=True)
    author = models.CharField(max_length=500, blank=True)
    content = models.TextField()
    word_count = models.IntegerField(default=0)
    index_table = models.TextField(blank=True)  # JSON : {mot: {occurrences, tfidf, score}}

    class Meta:
        ordering = ('gutenberg_id',)

    def get_index(self):
        return json.loads(self.index_table) if self.index_table else {}