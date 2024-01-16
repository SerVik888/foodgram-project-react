from django.db.models import Q
from django_filters import CharFilter, FilterSet

from recipes.models import Ingredient, Recipe


class IngredientSearchFilter(FilterSet):
    """Фильтр для ингредиентов."""

    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeSearchFilter(FilterSet):
    """Фильтр для рецептов."""
    author = CharFilter(field_name='author')
    tags = CharFilter(method='tags_filter')
    is_favorited = CharFilter(method='is_favorited_filter')
    is_in_shopping_cart = CharFilter(method='is_in_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def tags_filter(self, queryset, name, value):
        """Получаем теги зависимо от query-параметров запроса."""
        tags = self.request.query_params.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()

    def is_favorited_filter(self, queryset, name, value):
        """Получаем рецепты которые находятся в избранном
        или все которых в избранном нет, зависимо от query-параметров запроса.
        """
        if value == '1' and self.request.user.id:
            return queryset.filter(
                is_favorited__user=self.request.user
            )
        elif value == '0' and self.request.user.id:
            return queryset.filter(
                ~Q(is_favorited__user=self.request.user)
            )
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        """Получаем рецепты которые находятся в списке покупок
        или все которых в списке нет, зависимо от query-параметров запроса.
        """
        if value == '1' and self.request.user.id:
            return queryset.filter(
                is_in_shopping_cart__user=self.request.user
            )
        elif value == '0' and self.request.user.id:
            return queryset.filter(
                ~Q(is_in_shopping_cart__user=self.request.user)
            )
        return queryset
