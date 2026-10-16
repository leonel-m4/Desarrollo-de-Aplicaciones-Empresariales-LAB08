from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Article, Category


def published_articles():
    return Article.objects.filter(published_at__lte=timezone.now()).select_related('author').prefetch_related('categories')


def portal_context():
    return {
        'categories': Category.objects.all(),
    }


def home(request):
    context = portal_context()
    context['articles'] = published_articles()
    return render(request, 'news/home.html', context)


def detail(request, slug):
    context = portal_context()
    article = get_object_or_404(published_articles(), slug=slug)
    context['article'] = article
    context['related_articles'] = (
        published_articles().filter(categories__in=article.categories.values_list('pk', flat=True))
        .exclude(pk=article.pk).distinct()[:3]
    )
    return render(request, 'news/detail.html', context)


def category(request, slug):
    selected_category = get_object_or_404(Category, slug=slug)
    context = portal_context()
    context.update({
        'selected_category': selected_category,
        'articles': published_articles().filter(categories=selected_category),
    })
    return render(request, 'news/category.html', context)
