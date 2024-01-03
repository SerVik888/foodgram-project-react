from django_filters import CharFilter, FilterSet

from recipes.models import Ingredient


class IngredientSearchFilter(FilterSet):
    """Фильтр для ингредиентов."""
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
