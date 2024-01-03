from django.contrib import admin

from users.models import CustomUser, Follow

admin.site.empty_value_display = 'Не задано'


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        'email',
        'username',
        'first_name',
        'last_name'
    )
    search_fields = (
        'email',
        'username'
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'following'
    )
