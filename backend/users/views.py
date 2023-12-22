from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
# from users.permissions import IsAdminOrSuperuser
from rest_framework.response import Response
from djoser.views import UserViewSet
from users.models import Follow
from users.serializers import CustomUserSerializer
# from users.utils import send_code
from rest_framework.pagination import PageNumberPagination

User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    """Обрабатывает запрос на получение, создание, редактирование,
    удаления пользователя и получение пользователей."""
    # queryset = User.objects.all()
    # serializer_class = CustomUserSerializer
    # pagination_class = LimitOffsetPagination
    # http_method_names = ('get', 'post')

    # NOTE Нужно будет переписать на другой
    # permission_classes = (AllowAny,)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)
    # lookup_field = 'username'
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        # serializer_class=CustomUserSerializer,
    )
    def subscriptions(self, request):
        # def get_queryset(self):
        """Получаем подписки принадлежащий пользователю."""
        subscribed_users = []
        subscribes = request.user.subscribers.all()
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(subscribes, request)

        for subscription in result_page:
            # Получаем связанного пользователя для каждой подписки
            subscribed_user = subscription.following
            subscribed_users.append(subscribed_user)
        serializer = self.get_serializer(
            subscribed_users, many=True
        )

        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        subscriber = get_object_or_404(User, id=id)

        if request.method == 'POST':
            serializer = self.get_serializer(subscriber)
            try:
                Follow.objects.create(
                    following=self.request.user,
                    user=subscriber,
                )
            except IntegrityError:
                return Response(
                    'Вы уже подписаны на этого пользователя'
                    ' или пытаетесь подписаться на себя!',
                    status.HTTP_400_BAD_REQUEST
                )
            return Response(serializer.data, status.HTTP_201_CREATED)

        subscription = Follow.objects.filter(
            following_id=self.request.user.id, user_id=id
        ).first()
        if not subscription:
            return Response(
                'Вы не подписаны на этого пользователя.',
                status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(None, status.HTTP_204_NO_CONTENT)


# class FollowViewSet(
#     mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
# ):
#     """Обрабатывает запрос на получение, создание, редактирование,
#     удаления одной подписки и получинея списка подписок автора
#     который отправил запрос.
#     """

#     serializer_class = FollowSerializer
#     # filter_backends = (DjangoFilterBackend, SearchFilter)
#     search_fields = ('following__username',)

#     def perform_create(self, serializer):
#         """При создании подписки меняем поле в ответе с числа на имя автора
#         или подпищика
#         """
#         serializer.save(user=self.request.user,)

#     def get_queryset(self):
#         """Получаем подписки принадлежащий пользователю."""
#         return self.request.user.subscribers.all()
