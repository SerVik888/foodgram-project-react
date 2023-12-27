from datetime import datetime
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.serializers import CustomUserSerializer
from recipes.models import FavoriteRecipe, Ingredient, Recipe, RecipeIngredient, RecipeTag, ShoppingIngredient, Tag
import base64  # Модуль с функциями кодирования и декодирования base64
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.http.request import QueryDict
User = get_user_model()


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
    amount = serializers.StringRelatedField(
        required=False
    )
    # amount = serializers.SerializerMethodField(
    #     required=False
    # )

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    # def get_amount(self, obj):
    #     # new_obj = get_object_or_404(RecipeIngredient, ingredient=obj, recipe=)
    #     return obj


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class CreateRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(Recipe.tags, many=True,
                         read_only=True)
    author = CustomUserSerializer(
        Recipe.author, read_only=True
    )
    ingredients = IngredientSerializer(
        Recipe.ingredients,
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

    def create(self, validated_data):
        # validate_ingredients = QueryDict('', mutable=True)
        ingredients = self.initial_data.pop('ingredients')
        tags_id = self.initial_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for id in tags_id:
            RecipeTag.objects.create(recipe=recipe, tag_id=id)
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient, id=ingredient.get('id')
            )
            ingredient['name'] = current_ingredient.name
            ingredient['measurement_unit'] = current_ingredient.measurement_unit
            RecipeIngredient.objects.create(
                ingredient_id=ingredient.get('id'), recipe=recipe, amount=ingredient.get('amount')
            )
        validated_data['id'] = recipe.id
        validated_data['ingredients'] = recipe.ingredients
        validated_data['tags'] = recipe.tags
        return validated_data

    def to_representation(self, instance):
        # instance.id = instance.get('id')
        representation = super().to_representation(instance)
        # representation = super().to_representation(instance)
        recipe = Recipe.objects.get(id=instance.get('id'))
        for ingredient in representation.get('ingredients'):

            current_ingredient = RecipeIngredient.objects.filter(
                ingredient_id=ingredient.get('id'), recipe_id=instance.get('id')
                # ingredient_id=ingredient.get('id'), recipe_id=representation.get('id')
            ).first()
            ingredient['amount'] = current_ingredient.amount
        return representation

    def get_is_favorited(self, obj):
        return False

    def get_is_in_shopping_cart(self, obj):
        return False


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(Recipe.tags, many=True,
                         read_only=True)
    # tags = serializers.SerializerMethodField()
    # author = serializers.SlugRelatedField(
    #     slug_field='username', read_only=True
    # )
    author = CustomUserSerializer(
        Recipe.author, read_only=True
    )
    ingredients = IngredientSerializer(
        Recipe.ingredients,
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

    # def create(self, validated_data):
    #     validate_ingredients = QueryDict('', mutable=True)
    #     ingredients = self.initial_data.pop('ingredients')
    #     tags_id = self.initial_data.pop('tags')
    #     recipe = Recipe.objects.create(**validated_data)
    #     for id in tags_id:
    #         RecipeTag.objects.create(recipe=recipe, tag_id=id)
    #     for ingredient in ingredients:
    #         current_ingredient = get_object_or_404(
    #             Ingredient, id=ingredient.get('id')
    #         )
    #         ingredient['name'] = current_ingredient.name
    #         ingredient['measurement_unit'] = current_ingredient.measurement_unit
    #         RecipeIngredient.objects.create(
    #             ingredient_id=ingredient.get('id'), recipe=recipe, amount=ingredient.get('amount')
    #         )
    #     # new_dict = validate_ingredients.update(
    #     #     ingredients)
    #     # validated_data['author'] = 1
    #     validated_data['id'] = recipe.id
    #     validated_data['ingredients'] = recipe.ingredients
    #     validated_data['tags'] = recipe.tags
    #     return validated_data

    # def get_instance(self, ingredients):
    #     return ingredients

    def to_representation(self, instance):
        # instance.id = instance.get('id')
        representation = super().to_representation(instance)
        # representation = super().to_representation(instance)
        # representation['id'] =
        for ingredient in representation.get('ingredients'):

            current_ingredient = RecipeIngredient.objects.filter(
                ingredient_id=ingredient.get('id'), recipe_id=instance.id
                # ingredient_id=ingredient.get('id'), recipe_id=representation.get('id')
            ).first()
            ingredient['amount'] = current_ingredient.amount
        return representation
        # return representation
    # def to_representation(self, instance):
    #     """
    #     Object instance -> Dict of primitive datatypes.
    #     """
    #     ret = OrderedDict()
    #     fields = self._readable_fields

    #     for field in fields:
    #         try:
    #             attribute = field.get_attribute(instance)
    #         except SkipField:
    #             continue

        # We skip `to_representation` for `None` values so that fields do
        # not have to explicitly deal with that case.
        #
        # For related fields with `use_pk_only_optimization` we need to
        # resolve the pk value.
        #     check_for_none = attribute.pk if isinstance(
        #         attribute, PKOnlyObject) else attribute
        #     if check_for_none is None:
        #         ret[field.field_name] = None
        #     else:
        #         ret[field.field_name] = field.to_representation(attribute)

        # return ret

    # def get_tags(self, obj):
    #     tags = self.initial_data.get('tags')
    #     current_tags = []
    #     for id in tags:
    #         tag = get_object_or_404(Tag, id=id)
    #         current_tags.append(tag)

    #     serializer = TagSerializer(current_tags, many=True)
    #     return serializer.data

    # def get_ingredients(self, obj):

    #     serializer = IngredientSerializer(obj.ingredients, many=True)
    #     return serializer.data

    def get_is_favorited(self, obj):
        favorite = FavoriteRecipe.objects.filter(
            user=self.context.get('request').user, recipe=obj
        ).first()
        if favorite:
            return True
        else:
            return False

    def get_is_in_shopping_cart(self, obj):
        buy = ShoppingIngredient.objects.filter(
            user=self.context.get('request').user, recipe=obj
        ).first()
        if buy:
            return True
        else:
            return False


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
