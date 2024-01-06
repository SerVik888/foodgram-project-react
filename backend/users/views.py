from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api.pagination import PageSizeNumberPagination
from api.permissions import IsOwnerOrReadOnly
from users.models import Follow

User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    """Обрабатывает запрос на получение, создание, редактирование,
    удаления пользователей и подписок."""

    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    pagination_class = PageSizeNumberPagination

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Получаем данные пользователя сделавшего запрос."""
        return super().me(request)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Получаем подписки принадлежащий пользователю."""

        subscribed_users = []
        subscribes = request.user.followings.all()
        paginator = PageSizeNumberPagination()
        result_page = paginator.paginate_queryset(subscribes, request)

        for subscription in result_page:
            # Получаем связанного пользователя для каждой подписки
            subscribed_user = subscription.user
            # subscribed_user = subscription.following
            subscribed_users.append(subscribed_user)

        serializer = self.get_serializer(
            subscribed_users, many=True
        )

        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        """Создаём или удаляем подписку."""
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
        return Response('Подписка удалена.', status.HTTP_204_NO_CONTENT)
