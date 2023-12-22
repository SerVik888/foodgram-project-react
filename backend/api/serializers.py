from datetime import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.serializers import CustomUserSerializer
from recipes.models import Ingredient, Recipe, RecipeTag, Tag
import base64  # Модуль с функциями кодирования и декодирования base64
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Если полученный объект строка, и эта строка
        # начинается с 'data:image'...
        if isinstance(data, str) and data.startswith('data:image'):
            # ...начинаем декодировать изображение из base64.
            # Сначала нужно разделить строку на части.
            format, imgstr = data.split(';base64,')
            # И извлечь расширение файла.
            ext = format.split('/')[-1]
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):

    # tags = TagSerializer(many=True)
    tags = serializers.SerializerMethodField()
    # tags = serializers.PrimaryKeyRelatedField(
    #     # pk_field='id',
    #     queryset=Tag.objects.all(),
    #     # read_only=True,
    #     many=True
    # )
    # author = serializers.SlugRelatedField(
    #     slug_field='username',
    #     read_only=True
    # )
    author = CustomUserSerializer(
        read_only=True
    )
    # ingredients = serializers.PrimaryKeyRelatedField(
    #     # pk_field='id',
    #     queryset=Ingredient.objects.all(),
    #     many=True
    # )
    ingredients = IngredientSerializer(
        many=True,
        read_only=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
    #  def _get_children(self, obj):
    #      serializer = ChildSerializer(obj.child_list(), many=True)
    #      return serializer.data

    def create(self, validated_data):
        tags = self.initial_data.get('tags')

        recipe = Recipe.objects.create(**validated_data)

        for id in tags:
            tag = get_object_or_404(Tag, id=id)

            RecipeTag.objects.create(
                tag=tag, recipe=recipe)
        return recipe

    def get_tags(self, obj):
        tags = self.initial_data.get('tags')
        current_tags = []
        for id in tags:
            tag = get_object_or_404(Tag, id=id)
            current_tags.append(tag)

        serializer = TagSerializer(current_tags, many=True)
        return serializer.data

    def get_ingredients(self, obj):
        return obj

    def get_is_favorited(self, obj):
        return False

    def get_is_in_shopping_cart(self, obj):
        return False
