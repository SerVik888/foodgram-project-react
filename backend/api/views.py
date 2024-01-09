from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api.filters import IngredientSearchFilter
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (
    CreateUpdateRecipeSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer
)
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingIngredient,
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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,)

    def get_serializer_class(self):
        """Выбирает сериализатор, в зависимости от метода запроса."""
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateUpdateRecipeSerializer

    def get_queryset(self):
        """Получаем рецепты зависимо от query-параметров запроса."""
        queryset = self.queryset
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        author_id = self.request.query_params.get('author')
        tags = self.request.query_params.getlist('tags')

        if tags and len(tags) < 3:
            queryset = Recipe.objects.filter(tags__slug__in=tags).distinct()

        if author_id:
            queryset = queryset.filter(
                author_id=int(author_id)
            )

        if is_favorited == '1' and self.request.user.id:
            queryset = queryset.filter(
                is_favorited__user=self.request.user
            )
        elif is_favorited == '0' and self.request.user.id:
            queryset = queryset.filter(
                ~Q(is_favorited__user=self.request.user)
            )

        if is_in_shopping_cart == '1' and self.request.user.id:
            queryset = Recipe.objects.filter(
                is_in_shopping_cart__user=self.request.user
            )
        elif is_in_shopping_cart == '0' and self.request.user.id:
            queryset = Recipe.objects.filter(
                ~Q(is_in_shopping_cart__user=self.request.user)
            )
        return queryset

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Добвляем или удаляем рецепт из избранного."""
        favorite = FavoriteRecipe.objects.filter(
            user=request.user, recipe_id=pk
        ).first()

        if request.method == 'POST':
            recipe = Recipe.objects.filter(id=pk).first()
            if not recipe:
                return Response(
                    'Такой рецепт не найден!',
                    status.HTTP_400_BAD_REQUEST
                )
            if favorite:
                return Response(
                    'Рецепт уже добавлен в избранное.',
                    status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.create(
                user=request.user, recipe=recipe
            )
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Recipe, id=pk)
        if not favorite:
            return Response(
                'Такого рецепта нет в избранном.', status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(
            'Рецепт удалён из избранного.', status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Добавляем или удаляем рецепт из списка покупок."""
        if request.method == 'POST':
            recipe = Recipe.objects.filter(id=pk).first()
            if not recipe:
                return Response(
                    'Такой рецепт не найден!',
                    status.HTTP_400_BAD_REQUEST
                )
            buy = ShoppingIngredient.objects.filter(
                user=request.user, recipe=recipe
            ).first()
            if buy:
                return Response(
                    'Рецепт уже добавлен в список покупок.',
                    status.HTTP_400_BAD_REQUEST
                )

            for ingredient in recipe.ingredients.all():
                amount = RecipeIngredient.objects.filter(
                    ingredient=ingredient, recipe=recipe
                ).first().amount
                ShoppingIngredient.objects.create(
                    user=request.user,
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount
                )
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        recipe = get_object_or_404(Recipe, id=pk)
        buy = ShoppingIngredient.objects.filter(
            user=request.user, recipe=recipe
        ).first()
        if not buy:
            return Response(
                'Такого рецепта нет в списке покупок.',
                status.HTTP_400_BAD_REQUEST
            )
        ShoppingIngredient.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        return Response(
            'Рецепт удалён из списка покупок.', status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок в файле."""
        purchases_list = []
        purchases = {}
        purchase_models = ShoppingIngredient.objects.filter(user=request.user)

        for purchase in purchase_models:
            name = purchase.ingredient.name
            amount = purchase.amount
            if name in purchases:
                purchases[name] += amount
            else:
                purchases[name] = amount

        for name, amount in purchases.items():
            string = f'- {name}: {amount}'
            purchases_list.append(string)

        purchases_list = '\n'.join(purchases_list)
        response = HttpResponse(purchases_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format('shoppint_list.txt')
        )
        response.content = purchases_list.encode('cp1251')

        return response

    @action(
        detail=False,
        methods=['get'],
    )
    def clear_table(self, request):
        # TODO Это временный action для очистки таблицы
        Recipe.objects.all().delete()

        return Response(
            'Таблица рецептов очищена',
            status.HTTP_200_OK
        )
