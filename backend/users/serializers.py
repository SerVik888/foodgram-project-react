from django.contrib.auth import get_user_model
from django.forms import ValidationError
from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer

from users.models import Follow
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
# from users.views import FollowViewSet

User = get_user_model()


class CustomUserSerializer(UserSerializer, serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    # following = SlugRelatedField(
    #     slug_field='user', queryset=Follow.objects.all()
    # )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        # request = self.context.get('request').user
        # aaa = self.instance
        is_subscribed = User.objects.filter(
            subscribers__user=obj).first()
        # subscriber = obj.subscribers.instance.id
        # is_subscribe = request.subscribers.instance.id
        # is_subscribed = Follow.objects.filter(
        #     following_id=subscriber, user_id=is_subscribe
        # ).first()
        if is_subscribed:
            return True
        else:
            return False
        # id = subscriber.get('following_id')
        # is_id = is_subscribe.get('following_id')
        # url1 = self.context('data')
        # data1 = self.data.get('id')
        # request = self.context['view'].kwargs.get('id')
        # url = request.kwargs
        # return False

    # def validate_is_subscribed(self, data):
        # """Проверяем что пользователь не подписывается на самого себя."""
        # if self.context.get('request').user == following:
        #     raise ValidationError(
        #         'Вы не можете подписаться на себя.'
        #     )
        # return following


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }


# class FollowSerializer(serializers.ModelSerializer):

#     user = SlugRelatedField(read_only=True, slug_field='username')

#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'first_name', 'last_name',)
#         validators = [
#             serializers.UniqueTogetherValidator(
#                 queryset=Follow.objects.all(),
#                 fields=('user', 'following')
#             )
#         ]

#     def validate_following(self, following):
#         """Проверяем что пользователь не подписывается на самого себя."""
#         if self.context.get('request').user == following:
#             raise ValidationError(
#                 'Вы не можете подписаться на себя.'
#             )
#         return following
