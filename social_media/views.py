
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import Profile, Post, PostLike, PostComment
from social_media.permissions import IsOwner
from social_media.tasks import post_create_delay
from social_media_service.celery import debug_task

from social_media.serializers import (
    ProfileSerializer,
    ProfileFollowerSerializer,
    ProfileDetailSerializer,
    ProfileListSerializer,
    ProfileImageSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostImageSerializer,
    PostCommentCreateSerializer,
    PostCommentListSerializer
)


class ProfileViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Profile.objects
    serializer_class = ProfileDetailSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the profiles with filters"""
        bio = self.request.query_params.get("bio")
        address = self.request.query_params.get("address")
        username = self.request.query_params.get("username")

        queryset = self.queryset

        if bio:
            queryset = queryset.filter(bio__icontains=bio)

        if address:
            queryset = queryset.filter(address__icontains=address)

        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer

        if self.action == "retrieve":
            return ProfileDetailSerializer

        if self.action == "upload_image":
            return ProfileImageSerializer

        return ProfileSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAuthenticated],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific profile"""
        movie = self.get_object()
        serializer = self.get_serializer(movie, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "address",
                type=OpenApiTypes.STR,
                description="Filter by profile address (ex. ?address=Oslo)",
            ),
            OpenApiParameter(
                "username",
                type=OpenApiTypes.STR,
                description="Filter by profile username (ex. ?username=Newbie)",
            ),
            OpenApiParameter(
                "bio",
                type=OpenApiTypes.STR,
                description="Filter by profile bio (ex. ?bio=User)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Post.objects.prefetch_related("likes", "comments")
    serializer_class = PostListSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        """Retrieve the posts with filters"""
        title = self.request.query_params.get("title")
        text = self.request.query_params.get("text")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if text:
            queryset = queryset.filter(text__icontains=text)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer

        if self.action == "upload_image":
            return PostImageSerializer

        return PostDetailSerializer
    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAuthenticated],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific post"""
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=True,
        url_path="like",
        permission_classes=[IsAuthenticated],
    )
    def like(self, request, pk=None):
        """Endpoint to like  specific post"""
        post = self.get_object()
        user = self.request.user
        like = PostLike.objects.filter(post=post, user=user)
        if like:
            like.delete()
        PostLike.objects.create(post=post, user=user)
        post = self.get_object()
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="unlike",
        permission_classes=[IsAuthenticated],
    )
    def unlike(self, request, pk=None):
        """Endpoint to unlike  specific post"""
        post = self.get_object()
        user = self.request.user
        like = PostLike.objects.filter(post=post, user=user)
        if like:
            like.delete()
        post = self.get_object()
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path="liked",
        permission_classes=[IsAuthenticated],
    )
    def liked(self, request, pk=None):
        """Endpoint to view liked posts"""
        likes = PostLike.objects.filter(user=self.request.user)
        posts = Post.objects.filter(id__in=likes.values_list('post', flat=True))
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="comment",
        permission_classes=[IsAuthenticated],
    )
    def comment(self, request, pk=None):
        """Endpoint to add comment to post"""
        serializer = PostCommentCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=self.request.user, post=self.get_object())
            post = self.get_object()
            post_serializer = self.get_serializer(post)

            return Response(post_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type=OpenApiTypes.STR,
                description="Filter by post title (ex. ?title=War)",
            ),
            OpenApiParameter(
                "text",
                type=OpenApiTypes.STR,
                description="Filter by post text (ex. ?text=USA)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        if serializer.validated_data.get("seconds") is not None:
            post_create_delay.apply_async(
                (serializer.validated_data, self.request.user.id),
                countdown=serializer.validated_data.get("seconds")
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            serializer.save(user=self.request.user)


class PostCommentViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = PostComment.objects.all()
    serializer_class = PostCommentListSerializer
    permission_classes = (IsOwner,)

    def get_serializer_class(self):
        if self.action == "update":
            return PostCommentCreateSerializer

        return PostCommentListSerializer

