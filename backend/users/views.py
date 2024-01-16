from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import PageSizeNumberPagination
from users.models import Follow

User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    """Обрабатывает запрос на получение, создание, редактирование,
    удаления пользователей и подписок."""

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
            subscribed_user = subscription.user
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
        request.data['method'] = request.method
        subscriber = User.objects.filter(id=id).first()
        serializer = self.get_serializer(
            subscriber, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if request.method == 'POST':
            Follow.objects.create(
                following=self.request.user,
                user=subscriber,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        Follow.objects.filter(
            following_id=self.request.user.id, user_id=id
        ).delete()
        return Response('Подписка удалена.', status.HTTP_204_NO_CONTENT)
