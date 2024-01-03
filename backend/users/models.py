from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from foodgram.settings import USER_EMAIL_MAX_LENGHT, USER_NAME_MAX_LENGTH


class CustomUser(AbstractUser):

    email = models.EmailField(
        max_length=USER_EMAIL_MAX_LENGHT,
        unique=True,
        verbose_name='Электронная почта'
    )
    username = models.CharField(
        max_length=USER_NAME_MAX_LENGTH, unique=True,
        verbose_name='Ник-нейм пользователя',
        validators=[
            RegexValidator(
                r'^[\w.@+-]+\Z',
                'Вы не можете зарегестрировать пользователя с таким именем.'
            ),
            RegexValidator(
                '^me$',
                'Вы не можете зарегестрировать пользователя с таким именем.',
                inverse_match=True
            ),

        ]
    )
    first_name = models.CharField(
        max_length=USER_NAME_MAX_LENGTH, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=USER_NAME_MAX_LENGTH, verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=USER_NAME_MAX_LENGTH, verbose_name='Пароль'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        default_related_name = 'users',

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='followings',
        verbose_name='Пользователь'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'), name='unique_user_and_following'
            ),
            models.CheckConstraint(
                name='subscriber_is_not_following',
                check=~models.Q(user_id=models.F("following_id")),
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.following}'
