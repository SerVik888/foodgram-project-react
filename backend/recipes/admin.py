from django.contrib import admin
from django.utils.html import format_html

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    ShoppingIngredient,
    Tag
)

admin.site.empty_value_display = 'Не задано'

NUM_OF_WORDS_OF_NAME = 3
NUM_OF_WORDS_OF_TEXT = 10


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = (
        'get_short_name',
        'author',
        'get_short_text',
        'cooking_time',
        'get_favorite_count',
        'image_tag',
    )
    search_fields = ('name',)
    list_filter = ('author', 'tags',)

    @admin.display(description='Название')
    def get_short_name(self, obj):
        """Получаем начальные слова названия рецепта."""
        return " ".join(obj.name.split()[:NUM_OF_WORDS_OF_NAME])

    @admin.display(description='Описание')
    def get_short_text(self, obj):
        """Получаем начальные слова описания рецепта."""
        return f'{" ".join(obj.text.split()[:NUM_OF_WORDS_OF_TEXT])} ...'

    @admin.display(description='Изображение')
    def image_tag(self, obj):
        """Получаем изображение рецепта."""
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="50" />'.format(obj.image.url)
            )
        return 'Не найдено'

    @admin.display(description='Описание')
    def get_favorite_count(self, obj):
        """Сколько раз рецепт добавлен в избранное."""
        return FavoriteRecipe.objects.filter(recipe=obj).count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = (
        'get_short_name',
        'measurement_unit',
    )
    search_fields = ('name',)

    @admin.display(description='Название')
    def get_short_name(self, obj):
        """Получаем начальные слова названия ингредиента."""
        return " ".join(obj.name.split()[:NUM_OF_WORDS_OF_NAME])


admin.site.register(Tag)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingIngredient)
