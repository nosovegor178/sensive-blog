from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Count
from django.db.models import Prefetch


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts__count,
    }


def index(request):
    popular_tags = Tag.objects.get_popular_tags()[:5]
    most_popular_posts = Post.objects.popular_posts()\
        .prefetch_related('author')[:5]\
        .prefetch_related(Prefetch(
                            'tags',
                            queryset=Tag.objects.
                            get_popular_tags()))[:5]\
        .fetch_with_comments_count()
    fresh_posts = Post.objects.prefetch_related('author')\
        .order_by('published_at')\
        .prefetch_related(Prefetch(
            'tags',
            queryset=Tag.objects.get_popular_tags()))\
        .fetch_with_comments_count()
    most_fresh_posts = list(fresh_posts)[-5:]
    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.annotate(Count('likes')).get(slug=slug)
    comments = Comment.objects.filter(post=post).select_related('author')
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })
    related_tags = Tag.objects.get_popular_tags()
    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes.count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }
    most_popular_tags = Tag.objects.get_popular_tags()[:5]
    most_popular_posts = Post.objects.popular_posts()\
        .prefetch_related('author')[:5]\
        .prefetch_related(Prefetch(
            'tags',
            queryset=Tag.objects.annotate(Count('posts'))))[:5]\
        .fetch_with_comments_count()
    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.get_popular_tags()[:5]

    most_popular_posts = Post.objects.popular_posts()\
        .prefetch_related('author')[:5]\
        .prefetch_related(Prefetch(
            'tags',
            queryset=Tag.objects.
            annotate(Count('posts'))))[:5]\
        .fetch_with_comments_count()

    related_posts = Post.objects.popular_posts()\
                        .prefetch_related('author')[:20]\
                        .prefetch_related(Prefetch(
                            'tags',
                            queryset=Tag.objects.
                            annotate(Count('posts'))))[:5]\
                        .fetch_with_comments_count()
    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})
