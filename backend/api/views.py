from rest_framework.response import Response
from urllib.parse import quote
from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from api.serializers import CreateRecipeSerializer, FavoriteSerializer, IngredientSerializer, RecipeSerializer, TagSerializer
from api.pagination import PageSizeNumberPagination
# from api.filters import CustomSearchFilter
from recipes.models import FavoriteRecipe, Ingredient, Recipe, RecipeIngredient, ShoppingIngredient, Tag
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework import permissions, viewsets, filters, status
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
# from api.permissions import AdminModeratorOwnerOrReadOnly, IsAdminOrReadOnly


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    # permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    http_method_names = ('delete', 'get', 'patch', 'post')
    # filter_backends = (CustomSearchFilter,)
    pagination_class = PageSizeNumberPagination
    # filterset_fields = ('author',)

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
        )

    def get_serializer_class(self):
        """Выбирает сериализатор, в зависимости от метода запроса."""
        if self.request.method == ('GET' or 'DELETE'):
            return RecipeSerializer
        return CreateRecipeSerializer

    def get_queryset(self):
        queryset = self.queryset
        # Добыть параметр color из GET-запроса
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        author_id = self.request.query_params.get('author')
        tags = self.request.query_params.get('tags')

        if tags:
            queryset = Recipe.objects.filter(
                tags_slug=tags
            )
        if author_id:
            queryset = Recipe.objects.filter(
                author_id=int(author_id)
            )
        if is_favorited == '1':
            queryset = Recipe.objects.filter(
                is_favorited__user=self.request.user
            )
        elif is_favorited == '0':
            queryset = Recipe.objects.filter(
                ~Q(is_favorited__user=self.request.user)
            )
        if is_in_shopping_cart == '1':
            queryset = Recipe.objects.filter(
                is_in_shopping_cart__user=self.request.user
            )
        elif is_in_shopping_cart == '0':
            queryset = Recipe.objects.filter(
                ~Q(is_in_shopping_cart__user=self.request.user)
            )
        return queryset

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        # FavoriteRecipe.objects.all().delete()
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = FavoriteRecipe.objects.filter(
            user=request.user, recipe=recipe
        ).first()

        if request.method == 'POST':
            if favorite:
                return Response(
                    'Рецепт уже добавлен в избранное.',
                    status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.create(
                user=request.user, recipe=recipe
            )
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data)

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
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        # ShoppingIngredient.objects.all().delete()
        recipe = get_object_or_404(Recipe, id=pk)
        buy = ShoppingIngredient.objects.filter(
            user=request.user, recipe=recipe
        ).first()

        if request.method == 'POST':
            if buy:
                return Response(
                    'Рецепт уже добавлен в список покупок.',
                    status.HTTP_400_BAD_REQUEST
                )
            # FavoriteRecipe.objects.create(
            #     user=request.user, recipe=recipe
            # )
            # ingredients = recipe.ingredients.all()
            for ingredient in recipe.ingredients.all():
                amount = RecipeIngredient.objects.get(
                    ingredient=ingredient, recipe=recipe
                ).amount
                ShoppingIngredient.objects.create(
                    user=request.user,
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount
                )
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data)

        if not buy:
            return Response(
                'Такого рецепта нет в списке покупок.', status.HTTP_400_BAD_REQUEST
            )
        ShoppingIngredient.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        return Response(
            'Рецепт удалён из списка покупок.', status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        purchases_list = []
        purchases = {}
        purchase_models = ShoppingIngredient.objects.filter(user=request.user)
        for purchase in purchase_models:

            name = purchase.ingredient.name
            amount = purchase.amount
            # purchases_list = [*purchases_list, [name, amount]]
            if name in purchases:
                purchases[name] += amount
            else:
                purchases[name] = amount
        for name, amount in purchases.items():
            string = f'- {name}: {amount}'
            purchases_list.append(string)
            # purchases_list[name] = amount
        # purchases_list
        # TODO Разобрать этот код
        purchases_list = '\n'.join(purchases_list)
        filename = 'my-purchases.txt'
        quoted_filename = quote(filename)
        response = HttpResponse(purchases_list, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="{quoted_filename}"'
        )
        # filename = "my-purchases.txt"
        # response = HttpResponse(
        #     purchases_list, content_type='text/plain'
        # )
        # response['Content-Disposition'] = 'attachment; filename={0}'.format(
        #     filename)
        return response
        # with open('outfile.txt', 'w') as fw:
        #     fw.write(purchases_list)
        # content = open("uploads/something.txt").read()
        # return HttpResponse(purchases_list, content_type='text/plain')

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
