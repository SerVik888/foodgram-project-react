import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingIngredient,
    Tag
)
from users.serializers import CustomUserSerializer

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Сериалайзер для обработки картинок."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientAmongSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        required=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class IngredientSerializer(serializers.ModelSerializer):
    amount = serializers.StringRelatedField(
        required=False
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True,
                         read_only=True)
    author = CustomUserSerializer(
        Recipe.author, read_only=True
    )
    ingredients = IngredientSerializer(
        many=True,
        read_only=True
    )
    image = Base64ImageField(required=True)
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for ingredient in representation.get('ingredients'):
            current_ingredient = RecipeIngredient.objects.filter(
                ingredient_id=ingredient.get('id'), recipe_id=instance.id
            ).first()
            ingredient['amount'] = current_ingredient.amount
        return representation

    def get_is_favorited(self, obj):
        if self.context and self.context.get('request').user.id:
            favorite = FavoriteRecipe.objects.filter(
                user=self.context.get('request').user, recipe=obj
            ).first()
            if favorite:
                return True
            else:
                return False
        else:
            return False

    def get_is_in_shopping_cart(self, obj):
        if self.context and self.context.get('request').user.id:
            is_in_shopping_cart = ShoppingIngredient.objects.filter(
                user=self.context.get('request').user, recipe=obj
            ).first()
            if is_in_shopping_cart:
                return True
            else:
                return False
        else:
            return False


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
        allow_empty=False
    )
    author = CustomUserSerializer(
        Recipe.author, read_only=True
    )
    ingredients = IngredientAmongSerializer(
        many=True,
        required=True, allow_empty=False
    )
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient_id=ingredient.get('id').id,
                recipe=recipe,
                amount=ingredient.get('amount')
            )

        return recipe

    def update(self, instance, validated_data):
        recipe = get_object_or_404(
            Recipe, id=instance.id
        )
        ingredients = validated_data.get('ingredients')
        tags = validated_data.get('tags')
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.update_or_create(
                ingredient_id=ingredient.get('id').id,
                recipe=recipe,
                defaults={"amount": ingredient.get('amount')}
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data

    def validate_tags(self, value):
        if len(value) != len(list(set(value))):
            raise ValidationError('Нельзя добавлять одинаковые теги!')
        return value

    def validate_ingredients(self, value):
        ingredients_id = []
        for ingredient in value:
            ingredients_id.append(ingredient.get('id'))
        if len(ingredients_id) != len(list(set(ingredients_id))):
            raise ValidationError('Нельзя добавлять одинаковые ингредиенты!')
        return value

    def validate(self, data):
        if not data.get('tags') or not data.get('ingredients'):
            raise ValidationError(
                'Отсутствует поле с тегами или ингредиентами!'
            )
        return data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
