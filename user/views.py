from rest_framework import generics
from rest_framework import status

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.views import APIView

from user.serializers import UserSerializer
from social_media.serializers import (
    UserFollowingSerializer,
    ProfileSerializer,
    PostListSerializer
)
from social_media.models import UserFollowing, Profile, Post


class LogoutView(APIView):
    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    permission_classes = (AllowAny,)


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class CreateUserFollowingView(generics.CreateAPIView):
    serializer_class = UserFollowingSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user_id=self.kwargs['pk'], following_user_id=self.request.user.id)


class DeleteUserFollowingView(APIView):
    serializer_class = UserFollowingSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None, **kwargs):
        obj = UserFollowing.objects.get(
            user_id=self.kwargs['pk'],
            following_user_id=self.request.user.id
        )
        obj.delete()
        return Response(status=status.HTTP_200_OK)


class MyFollowersView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None, **kwargs):
        followers = UserFollowing.objects.filter(
                user_id=self.request.user.id
            )
        self.queryset = Profile.objects.filter(
            user_id__in=followers.values_list('following_user_id', flat=True)
        )
        return self.list(request, **kwargs)


class MyFollowingView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None, **kwargs):
        following = UserFollowing.objects.filter(
                following_user_id=self.request.user.id
            )
        self.queryset = Profile.objects.filter(
            user_id__in=following.values_list('user_id', flat=True)
        )
        return self.list(request, **kwargs)


class MyPostsView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None, **kwargs):
        self.queryset = Post.objects.filter(
            user=self.request.user)
        return self.list(request, **kwargs)


class MyFollowingPostsView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None, **kwargs):
        following = UserFollowing.objects.filter(
                following_user_id=self.request.user.id
            )
        self.queryset = Post.objects.filter(
            user__in=following.values_list('user_id', flat=True)
        )
        return self.list(request, **kwargs)