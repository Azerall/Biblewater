# Generated by Django 5.1.7 on 2025-03-23 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mygutenberg', '0002_remove_booktext_pagerank_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booktext',
            name='title',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
