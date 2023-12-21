from django.urls import path
from user.views import (
    CreateUserView,
    LogoutView,
    CreateTokenView,
    ManageUserView,
    CreateUserFollowingView,
    DeleteUserFollowingView,
    MyFollowersView,
    MyFollowingView,
    MyPostsView,
    MyFollowingPostsView
)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", CreateTokenView.as_view(), name="login"),
    path("logout/", LogoutView.as_view()),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("me/posts/", MyPostsView.as_view(), name="my_posts"),
    path("me/follow/<int:pk>", CreateUserFollowingView.as_view(), name="follow"),
    path("me/unfollow/<int:pk>", DeleteUserFollowingView.as_view(), name="unfollow"),
    path("me/followers/", MyFollowersView.as_view(), name="my_followers"),
    path("me/following/", MyFollowingView.as_view(), name="my_following"),
    path("me/following/posts/", MyFollowingPostsView.as_view(), name="my_following_posts"),
]
app_name = "user"
