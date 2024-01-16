from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError

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
        if not self.context or not self.context.get('request').user.id:
            return False
        return obj.subscribers.filter(
            following_id=self.context.get('request').user.id,
            user_id=obj.subscribers.instance.id
        ).exists()

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

    def validate(self, data):
        method = self.initial_data.get('method')
        current_user = self.context.get('request').user
        subscribed = Follow.objects.filter(
            following=current_user, user=self.instance
        ).exists()

        if not self.instance:
            raise NotFound(detail='Такой пользователь не найден!', code=404)
        if (subscribed or current_user == self.instance) and method == 'POST':
            raise ValidationError(
                'Подписка уже существует или '
                'вы пытаетесь подписаться на самого себя.'
            )
        if not subscribed and method == 'DELETE':
            raise ValidationError('Такой подписки не существует.')
        return data


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }
