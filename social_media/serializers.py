from django.db import transaction
from rest_framework import serializers

from social_media.models import (
    Profile,
    Post,
    PostLike,
    PostComment,
    UserFollowing,
)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("bio", "address", "username")


class ProfileListSerializer(ProfileSerializer):
    class Meta:
        model = Profile
        fields = ("bio", "username")


class ProfileFollowerSerializer(ProfileSerializer):
    class Meta:
        model = Profile
        fields = ("username", )


class ProfileDetailSerializer(ProfileSerializer):
    followers = ProfileFollowerSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = (
            "bio", "address", "username", "followers", "image"
        )


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "image")


class UserFollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollowing
        fields = ()


class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ("user", "created_at")


class PostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = ("user", "text", "id")


class PostCommentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = ("user", "text", "id", "post")


class PostCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = ("text",)


class PostDetailSerializer(serializers.ModelSerializer):
    likes = PostLikeSerializer(many=True, read_only=True)
    comments = PostCommentSerializer(many=True, read_only=True)
    seconds = serializers.IntegerField(required=False)

    class Meta:
        model = Post
        fields = (
            "text", "title", "likes", "comments", "image", "seconds"
        )


class PostListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = (
            "user", "title"
        )


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "image")