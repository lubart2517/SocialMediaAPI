from django.contrib import admin

from social_media.models import Profile, Post, PostComment, PostLike, UserFollowing


@admin.register(UserFollowing)
class UserFollowing(admin.ModelAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    pass


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    pass