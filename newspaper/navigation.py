from newspaper.models import Post, Category, Tag


def navigation(request):
    categories = Category.objects.all()[:5]
    tags = Tag.objects.all()[:10]
    recent_post = Post.objects.filter(
        status="active", published_at__isnull=False
    ).order_by("-published_at", "-views_count")[:6]

    return {"recent_posts": recent_post, "tags": tags, "categories": categories}
