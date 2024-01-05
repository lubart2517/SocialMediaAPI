
from social_media.serializers import PostDetailSerializer
from user.models import User

from celery import shared_task


@shared_task
def post_create_delay(post_data, user_id):
    post = PostDetailSerializer(data=post_data)
    current_user = User.objects.get(id=user_id)
    post.save(user=current_user)
