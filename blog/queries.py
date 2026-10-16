"""Queries behind the views. Part 2 of the lab happens in this file."""
from blog.models import Post


def posts_for_front_page():
    # Join the single-valued author and fetch all many-to-many tags in one batch.
    return (
        Post.objects.filter(published=True)
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-published_at")
    )
