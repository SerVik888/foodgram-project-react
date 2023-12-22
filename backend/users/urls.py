# from rest_framework.authtoken import views
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from users.views import FoodgramUserViewSet

router_v1 = DefaultRouter()

# users_router_v1.register('users/', UserViewSet, basename='users')
# router_v1.register('subscribe', FollowViewSet, basename='follows')
router_v1.register("users", FoodgramUserViewSet)
# auth_router_v1.register('signup', RegistrationViewSet, basename='register')
# auth_router_v1.register('token', ConfirmCodeTokenViewSet, basename='get_token')

urlpatterns = [
    path('', include(router_v1.urls)),
    # path('', include('djoser.urls')),
    # path('?page', include(users_router_v1.urls)),

    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
