from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Тег', max_length=settings.PECIPE_NAME_MAX_LENGTH, unique=True,
    )
    color = ColorField(
        'Цвет', default=settings.RANDOM_COLOR_STRING, unique=True
    )
    slug = models.SlugField(
        'Слаг', max_length=settings.PECIPE_NAME_MAX_LENGTH, unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Ингредиент', max_length=settings.PECIPE_NAME_MAX_LENGTH)
    measurement_unit = models.CharField(
        'Еденица измерения',
        max_length=settings.PECIPE_NAME_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = 'ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name="unique_title_measurement_unit_pair"
            )
        ]

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
        max_length=settings.PECIPE_NAME_MAX_LENGTH
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
    cooking_time = models.PositiveSmallIntegerField(
        'Время',
        default=settings.MIN_COOKING_TIME,
        validators=[
            MaxValueValidator(settings.MAX_COOKING_TIME),
            MinValueValidator(settings.MIN_COOKING_TIME)
        ]
    )
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        default_related_name = 'tag_recipe'

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        default=settings.MIN_AMOUNT,
        validators=[
            MaxValueValidator(settings.MAX_AMOUNT),
            MinValueValidator(settings.MIN_AMOUNT)
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        default_related_name = 'recipe_ingredients'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class RecipeUserBase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name="unique_user_recipe_pair"
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class FavoriteRecipe(RecipeUserBase):

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'is_favorited'


class ShoppingRecipe(RecipeUserBase):

    class Meta:
        verbose_name = 'Ингредиент для покупки'
        verbose_name_plural = 'Ингредиенты для покупки'
        default_related_name = 'is_in_shopping_cart'
