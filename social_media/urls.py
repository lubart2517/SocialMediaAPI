from django.urls import path, include
from rest_framework import routers
from social_media.views import (
    ProfileViewSet,
    PostViewSet,
    PostCommentViewSet
)

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("posts", PostViewSet)
router.register("comments", PostCommentViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "social_media"
