from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator

User = get_user_model()

# TODO Незабудь положить длинну строк в переменные


class Tag(models.Model):
    name = models.CharField('Тег', max_length=200, unique=True, )
    color = models.CharField('Цвет', max_length=7, unique=True)

    slug = models.SlugField(
        'Тег',
        max_length=200,
        unique=True,
        validators=[
            RegexValidator(
                r'^[-a-zA-Z0-9_]+$'
                # Можно ответ потом написать.
            ),]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Ингредиент', max_length=200)
    measurement_unit = models.CharField(
        'Еденица измерения', max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        'Название', max_length=200
    )
    image = models.ImageField(
        upload_to='images/',
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        help_text='Удерживайте Ctrl для выбора нескольких вариантов'
    )
    tag = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Теги',
        help_text='Удерживайте Ctrl для выбора нескольких вариантов'
    )
    cooking_time = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(3600),
            MinValueValidator(1)
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
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
        default=1,
        validators=[
            MaxValueValidator(10000),
            MinValueValidator(1)
        ]
    )

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'
