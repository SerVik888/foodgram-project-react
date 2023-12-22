from django.db.models import Avg
from django.shortcuts import get_object_or_404
from api.serializers import IngredientSerializer, RecipeSerializer, TagSerializer
from recipes.models import Ingredient, Recipe, Tag
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import permissions, viewsets, filters, status
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
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

    # queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ('delete', 'get', 'patch', 'post')

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            # ingrediengs=self.request.data.get('ingredients')
        )

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
