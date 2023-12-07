from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import PostViewSet, UserViewSet

app_name = 'api-posts'

router = DefaultRouter()
router.register('posts', PostViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
