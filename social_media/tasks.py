from social_media.models import Post

from celery import shared_task


@shared_task
def count():
    return Post.objects.count()