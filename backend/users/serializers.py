from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe
from users.models import Follow

User = get_user_model()


class SubscribeRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CustomUserSerializer(UserSerializer, serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Подписан текущий пользователь на другого или нет."""
        request = self.context.get('request')
        return (
            not (not self.context or not request.user.is_authenticated)
            and obj.subscribers.filter(
                following_id=request.user.id,
                user_id=obj.subscribers.instance.id
            ).exists()
        )

    def to_representation(self, instance):
        """Добавляем рецепты и возможность менять их колличество в ответ."""
        representation = super().to_representation(instance)

        if self.context.get('request'):
            endpoint = self.context.get('request').build_absolute_uri()
            if 'subscribe' in endpoint or 'subscriptions' in endpoint:
                recipes_limit = self.context.get(
                    'request'
                ).query_params.get('recipes_limit')

                if recipes_limit:
                    recipes = instance.recipes.all()[:int(recipes_limit)]
                else:
                    recipes = instance.recipes.all()
                serializer = SubscribeRecipeSerializer(
                    recipes, many=True
                )
                representation['recipes'] = serializer.data
                representation['recipes_count'] = recipes.count()
        return representation


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('following', 'user')

    def to_representation(self, instance):
        return CustomUserSerializer(
            instance.user, context=self.context
        ).data

    def validate(self, data):
        subscribed = Follow.objects.filter(
            following=data.get('following'), user=data.get('user')
        ).exists()
        if subscribed or data.get('following') == data.get('user'):
            raise ValidationError(
                'Подписка уже существует или '
                'вы пытаетесь подписаться на самого себя.'
            )
        return data
