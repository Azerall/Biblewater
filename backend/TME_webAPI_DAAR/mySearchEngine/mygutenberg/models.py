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

    def __str__(self):
        return f"{self.gutenberg_id} - {self.title}"

class TrieNode(models.Model):
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        related_name='children'
    )
    char = models.CharField(max_length=1)
    is_end_of_word = models.BooleanField(default=False)
    word_data = models.BinaryField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['parent', 'char']),
        ]
        unique_together = ('parent', 'char')

    def set_word_data(self, data):
        if data:
            json_str = json.dumps(data)
            compressed = zlib.compress(json_str.encode('utf-8'))
            self.word_data = compressed
        else:
            self.word_data = None

    def get_word_data(self):
        if self.word_data:
            decompressed = zlib.decompress(self.word_data).decode('utf-8')
            return json.loads(decompressed)
        return {}

    def get_full_word(self):
        word = []
        node = self
        while node:
            word.append(node.char)
            node = node.parent
        return ''.join(reversed(word))

    @classmethod
    def search_by_prefix(cls, prefix):
        if not prefix:
            return []
        
        current_node = None
        for char in prefix.lower():
            if current_node is None:
                current_node = cls.objects.filter(parent__isnull=True, char=char).first()
            else:
                current_node = cls.objects.filter(parent=current_node, char=char).first()
            if not current_node:
                return []
        
        results = []
        cls._collect_words(current_node, results)
        return results

    @classmethod
    def _collect_words(cls, node, results, prefix=''):
        if not node:
            return
        
        current_prefix = prefix + node.char
        if node.is_end_of_word:
            results.append({
                'word': current_prefix,
                'data': node.get_word_data()
            })
        
        for child in node.children.all():
            cls._collect_words(child, results, current_prefix)

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
