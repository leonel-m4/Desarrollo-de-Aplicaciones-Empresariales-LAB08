from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from news.models import Article, Author

from .models import Genre, Movie, Rating


class PortalNavigationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.action = Genre.objects.create(name='Acción')
        cls.drama = Genre.objects.create(name='Drama')
        cls.comedy = Genre.objects.create(name='Comedia')
        cls.selected = Movie.objects.create(title='Película de referencia', release_year=2020)
        cls.top = Movie.objects.create(title='La más valorada', release_year=2024)
        cls.lower = Movie.objects.create(title='Otra película', release_year=2022)
        cls.extra = Movie.objects.create(title='Drama relacionado', release_year=2021)
        cls.unrelated = Movie.objects.create(title='Comedia sin coincidencias', release_year=2020)
        cls.unrated = Movie.objects.create(title='Pendiente de valoración', release_year=2023)
        cls.selected.genres.set([cls.action, cls.drama])
        cls.top.genres.set([cls.action, cls.drama])
        cls.lower.genres.add(cls.action)
        cls.extra.genres.add(cls.drama)
        cls.unrelated.genres.add(cls.comedy)
        cls.unrated.genres.add(cls.action)
        for movie, score in [(cls.selected, 4), (cls.top, 5), (cls.lower, 4), (cls.extra, 3), (cls.unrelated, 2)]:
            Rating.objects.create(movie=movie, score=score)
        author = Author.objects.create(name='Redacción de prueba')
        cls.article = Article.objects.create(
            title='Historia publicada', slug='historia-publicada', summary='Resumen', body='Texto',
            author=author, published_at=timezone.now() - timedelta(days=1),
        )
        cls.future = Article.objects.create(
            title='Historia futura', slug='historia-futura', summary='Resumen', body='Texto',
            author=author, published_at=timezone.now() + timedelta(days=1),
        )

    def test_home_introduces_both_sections_without_repeating_featured_content(self):
        response = self.client.get(reverse('movies:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['featured_movie'], self.top)
        self.assertNotIn(self.top, response.context['main_movies'])
        self.assertEqual(len(response.context['main_movies']), 4)
        self.assertEqual(response.context['featured_article'], self.article)
        self.assertNotIn(self.article, response.context['latest_articles'])
        self.assertNotContains(response, self.future.title)
        self.assertContains(response, self.article.get_absolute_url())
        self.assertContains(response, reverse('movies:catalog'))
        self.assertContains(response, reverse('news:home'))

    def test_recommendations_are_rated_related_unique_and_ordered(self):
        response = self.client.get(reverse('movies:recommendations', args=[self.selected.pk]))
        recommendations = list(response.context['recommendations'])
        self.assertEqual([movie.pk for movie in recommendations], [self.top.pk, self.lower.pk, self.extra.pk])
        self.assertEqual(recommendations[0].average_score, 5)
        self.assertEqual(recommendations[0].shared_genres, 2)
        self.assertTemplateUsed(response, 'components/movie_card.html')
        self.assertContains(response, 'Volver a películas')
        self.assertContains(response, reverse('movies:catalog'))

    def test_catalog_keeps_all_movies_and_their_genres(self):
        response = self.client.get(reverse('movies:catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['movie_count'], 6)
        genres = {genre.pk: [movie.pk for movie in genre.catalog_movies] for genre in response.context['genres']}
        self.assertIn(self.unrated.pk, genres[self.action.pk])
        self.assertEqual(genres[self.comedy.pk], [self.unrelated.pk])

    def test_empty_sections_remain_accessible(self):
        Article.objects.all().delete()
        Movie.objects.all().delete()
        Genre.objects.all().delete()
        self.assertEqual(self.client.get(reverse('movies:home')).status_code, 200)
        response = self.client.get(reverse('movies:catalog'))
        self.assertContains(response, 'El catálogo está por llegar.')
