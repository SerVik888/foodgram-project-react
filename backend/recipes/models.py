from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator
)
from django.db import models

from foodgram.settings import (
    COLOR_MAX_LENGTH,
    MAX_AMOUNT,
    MAX_COOKING_TIME,
    MIN_AMOUNT,
    MIN_COOKING_TIME,
    PECIPE_NAME_MAX_LENGTH
)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Тег',
        max_length=PECIPE_NAME_MAX_LENGTH,
        unique=True,
    )
    color = models.CharField('Цвет', max_length=COLOR_MAX_LENGTH, unique=True)

    slug = models.SlugField(
        'Тег',
        max_length=PECIPE_NAME_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                r'^[-a-zA-Z0-9_]+$',
                'Вы не можете создать такой slug.'
            ),
        ]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Ингредиент', max_length=PECIPE_NAME_MAX_LENGTH)
    measurement_unit = models.CharField(
        'Еденица измерения',
        max_length=PECIPE_NAME_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = 'ingredients'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        'Название',
        max_length=PECIPE_NAME_MAX_LENGTH
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/',
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        help_text='Удерживайте Ctrl для выбора нескольких вариантов'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Теги',
        help_text='Удерживайте Ctrl для выбора нескольких вариантов'
    )
    cooking_time = models.IntegerField(
        'Время',
        default=MIN_COOKING_TIME,
        validators=[
            MaxValueValidator(MAX_COOKING_TIME),
            MinValueValidator(MIN_COOKING_TIME)
        ]
    )
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(
        default=MIN_AMOUNT,
        validators=[
            MaxValueValidator(MAX_AMOUNT),
            MinValueValidator(MIN_AMOUNT)
        ]
    )

    class Meta:
        default_related_name = 'recipe_ingredients'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'is_favorited'

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingIngredient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(10000),
            MinValueValidator(1)
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент для покупки'
        verbose_name_plural = 'Ингредиенты для покупки'
        default_related_name = 'is_in_shopping_cart'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'
