from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

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
        """Подписан пользователь на текущего или нет."""
        if obj.id and self.context.get('request'):
            subscriber = obj.subscribers.instance.id
            is_subscribe = self.context.get('request').user.id
            is_subscribed = Follow.objects.filter(
                following_id=is_subscribe, user_id=subscriber
            ).first()
            if is_subscribed:
                return True
            else:
                return False
        return False

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
