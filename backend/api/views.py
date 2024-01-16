from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeSearchFilter
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (
    CreateUpdateRecipeSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer
)
from api.utils import download_file
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    ShoppingRecipe,
    Tag
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all()

    http_method_names = ('delete', 'get', 'patch', 'post')
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeSearchFilter

    def create_related_model(self, recipe, request, related_model):
        """Создать связанную модель для рецепта."""
        related_model.objects.create(
            user=request.user, recipe=recipe
        )

    def delete_record(self, recipe, request, model):
        """Удалить связанную модель для рецепта."""
        model.objects.filter(
            user=request.user, recipe=recipe
        ).delete()

    def use_favorite_serializer(
            self, request, pk, creat_func, delete_func, model
    ):
        request.data['model'] = model
        request.data['method'] = request.method
        request.data['user'] = request.user
        recipe = Recipe.objects.filter(id=pk).first()
        serializer = FavoriteSerializer(
            recipe, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if request.method == 'POST':
            creat_func(recipe, request, model)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        delete_func(recipe, request, model)
        return Response(
            'Рецепт удалён из избранного.', status.HTTP_204_NO_CONTENT
        )

    def get_serializer_class(self):
        """Выбирает сериализатор, в зависимости от метода запроса."""
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateUpdateRecipeSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Добвляем или удаляем рецепт из избранного."""
        return self.use_favorite_serializer(
            request,
            pk,
            self.create_related_model,
            self.delete_record,
            FavoriteRecipe
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Добавляем или удаляем рецепт из списка покупок."""
        return self.use_favorite_serializer(
            request,
            pk,
            self.create_related_model,
            self.delete_record,
            ShoppingRecipe
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Получить и скачать список покупок в файле."""
        purchases_list = self.queryset.filter(
            is_in_shopping_cart__user=request.user
        ).values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).order_by(
            'ingredients__name'
        ).annotate(
            amount=Sum('recipe_ingredients__amount')
        )
        shopping_list = '\n'.join(
            '- {}: {} {}.'.format(
                ingredient.get('ingredients__name'),
                ingredient.get('amount'),
                ingredient.get('ingredients__measurement_unit')
            )
            for ingredient in purchases_list
        )
        return download_file(shopping_list, 'shopping_list')
