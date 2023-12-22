import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Import data from CSV files into the database'

    def handle_ingredients(self, *args, **kwargs):
        with open('../data/ingredients.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            objs = [
                Ingredient(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
                for row in reader
            ]
            Ingredient.objects.bulk_create(objs)

    def handle_tags(self, *args, **kwargs):
        with open('../data/tags.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            objs = [
                Tag(
                    id=row['id'],
                    name=row['name'],
                    color=row['color'],
                    slug=row['slug'],
                )
                for row in reader
            ]
            Tag.objects.bulk_create(objs)

    def handle(self, *args, **kwargs):
        self.handle_ingredients()
        self.handle_tags()
