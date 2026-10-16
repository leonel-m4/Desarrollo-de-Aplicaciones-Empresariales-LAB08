from django.db.models import Avg, Count, F, Prefetch
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from news.models import Article

from .models import Genre, Movie


def home(request):
    movies = Movie.objects.prefetch_related('genres').annotate(average_score=Avg('ratings__score'))
    ranked_movies = movies.filter(average_score__isnull=False).order_by('-average_score', '-release_year', 'title')
    featured_movie = ranked_movies.first()
    main_movies = ranked_movies.exclude(pk=featured_movie.pk if featured_movie else None)[:4]
    articles = Article.objects.filter(published_at__lte=timezone.now()).select_related('author').prefetch_related('categories')
    featured_article = articles.first()
    latest_articles = articles.exclude(pk=featured_article.pk if featured_article else None)[:3]
    return render(
        request,
        'movies/home.html',
        {
            'movie_count': movies.count(),
            'featured_movie': featured_movie,
            'main_movies': main_movies,
            'featured_article': featured_article,
            'latest_articles': latest_articles,
        },
    )


def catalog(request):
    movies = Movie.objects.prefetch_related('genres').annotate(average_score=Avg('ratings__score'))
    genres = Genre.objects.prefetch_related(Prefetch('movies', queryset=movies, to_attr='catalog_movies'))
    return render(request, 'movies/catalog.html', {'genres': genres, 'movie_count': movies.count()})


def movie_recommendations(request, pk):
    movie = get_object_or_404(Movie.objects.select_related('director').prefetch_related('genres'), pk=pk)
    genre_ids = movie.genres.values_list('id', flat=True)
    recommendations = (
        Movie.objects.exclude(pk=movie.pk)
        .filter(genres__in=genre_ids)
        .annotate(average_score=Avg('ratings__score'), shared_genres=Count('genres', distinct=True))
        .filter(average_score__isnull=False)
        .prefetch_related('genres')
        .order_by(F('average_score').desc(nulls_last=True), '-shared_genres', 'title')
        .distinct()[:5]
    )
    return render(
        request,
        'movies/recommendations.html',
        {'movie': movie, 'recommendations': recommendations},
    )
