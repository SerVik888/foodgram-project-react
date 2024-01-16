from django.conf import settings
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.serializers import CustomUserSerializer

User = get_user_model()


class IngredientAmountSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        required=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', read_only=True
    )
    name = serializers.StringRelatedField(
        source='ingredient.name', read_only=True
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        source='recipe_ingredients', many=True, read_only=True
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

    def get_is_favorited(self, obj):
        if not self.context or not self.context.get('request').user.id:
            return False
        return obj.is_favorited.all().filter(
            user=self.context.get('request').user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        if not self.context or not self.context.get('request').user.id:
            return False
        return obj.is_in_shopping_cart.all().filter(
            user=self.context.get('request').user, recipe=obj
        ).exists()


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
        allow_empty=False
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        required=True, allow_empty=False
    )
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(
        required=True,
        min_value=settings.MIN_COOKING_TIME,
        max_value=settings.MAX_COOKING_TIME
    )

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

    def update_or_create_recipe_ingredients(self, recipe, ingredients):
        ingredients = [
            RecipeIngredient(
                ingredient_id=ingredient.get('id').id,
                recipe=recipe,
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        self.update_or_create_recipe_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        self.update_or_create_recipe_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data

    def validate_image(self, value):
        if not value:
            raise ValidationError('Нужно добавить изображение!')
        return value

    def validate_tags(self, value):
        if len(value) != len(list(set(value))):
            raise ValidationError('Нельзя добавлять одинаковые теги!')
        return value

    def validate(self, data):
        if not data.get('tags') or not data.get('ingredients'):
            raise ValidationError(
                'Отсутствует поле с тегами или ингредиентами!'
            )
        ingredients_id = [
            ingredient.get('id') for ingredient in data.get('ingredients')
        ]
        if len(ingredients_id) != len(list(set(ingredients_id))):
            raise ValidationError('Нельзя добавлять одинаковые ингредиенты!')
        return data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):

        if not self.instance and self.initial_data.get('method') == 'POST':
            raise ValidationError('Такой рецепт не найден!')
        elif not self.instance:
            raise NotFound(detail='Такой рецепт не найден!', code=404)

        is_model = self.initial_data.get('model').objects.filter(
            user=self.initial_data.get('user'), recipe=self.instance
        ).exists()

        if is_model and self.initial_data.get('method') == 'POST':
            raise ValidationError('Рецепт уже добавлен.')

        if not is_model and self.initial_data.get('method') == 'DELETE':
            raise ValidationError('Такого рецепта нет в списке.')
        return data
