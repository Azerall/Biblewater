from django.db import migrations
import json
import zlib

def recompress_word_data(apps, schema_editor):
    TrieNode = apps.get_model('mygutenberg', 'TrieNode')
    for node in TrieNode.objects.filter(is_end_of_word=True):
        if node.word_data:
            # Decompress existing data (likely compressed with default level)
            decompressed = zlib.decompress(node.word_data).decode('utf-8')
            data = json.loads(decompressed)
            # Re-compress with level=9
            json_str = json.dumps(data)
            node.word_data = zlib.compress(json_str.encode('utf-8'), level=9)
            node.save()

class Migration(migrations.Migration):
    dependencies = [('mygutenberg', '0001_initial')]  # Adjust to your last migration
    operations = [migrations.RunPython(recompress_word_data)]