from datetime import timedelta
from io import StringIO
from tempfile import TemporaryDirectory

from PIL import Image
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.db.models.deletion import ProtectedError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Article, Author, Category


class PortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name='Autora de prueba', biography='Biografía de prueba.')
        cls.category = Category.objects.create(name='Tecnología', slug='tecnologia')
        cls.article = Article.objects.create(
            title='Noticia publicada', slug='noticia-publicada', summary='Resumen de prueba.',
            body='<strong>Prueba</strong>\n<script>alert("prueba")</script>', author=cls.author,
            published_at=timezone.now() - timedelta(days=1),
        )
        cls.article.categories.add(cls.category)
        cls.admin = get_user_model().objects.create_superuser(
            username='prueba_admin', password='PruebaAdmin12345', email='admin@example.com',
        )

    def test_home_inherits_base_and_includes_card(self):
        response = self.client.get(reverse('news:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/base.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'components/navbar.html')
        self.assertTemplateUsed(response, 'news/_article_card.html')
        self.assertContains(response, reverse('news:detail', args=[self.article.slug]))
        self.assertContains(response, '/static/news/css/style.css')

    def test_body_is_escaped_and_linebreaks_remain(self):
        response = self.client.get(self.article.get_absolute_url())
        self.assertContains(response, '&lt;strong&gt;Prueba&lt;/strong&gt;')
        self.assertContains(response, '&lt;script&gt;')
        self.assertNotContains(response, '<script>alert("prueba")</script>')
        self.assertNotContains(response, '<strong>Prueba</strong>')
        self.assertContains(response, '<br>')

    def test_source_and_image_credits_are_displayed(self):
        self.article.source_name = 'Fuente de prueba'
        self.article.source_url = 'https://example.com/noticia/'
        self.article.image_credit = 'Fotografía de prueba'
        self.article.image_source_url = 'https://example.com/imagen.jpg'
        self.article.featured_image = 'news/articles/imagen.jpg'
        self.article.save()
        response = self.client.get(self.article.get_absolute_url())
        self.assertContains(response, 'https://example.com/noticia/')
        self.assertContains(response, 'https://example.com/imagen.jpg')
        self.assertContains(response, 'Fotografía de prueba')
        self.assertContains(response, 'Fuente original')

    def test_category_reuses_card_and_filters_articles(self):
        other = Category.objects.create(name='Cultura', slug='cultura')
        response = self.client.get(self.category.get_absolute_url())
        self.assertTemplateUsed(response, 'news/_article_card.html')
        self.assertEqual(list(response.context['articles']), [self.article])
        empty_response = self.client.get(other.get_absolute_url())
        self.assertContains(empty_response, 'Esta sección aún no tiene noticias.')

    def test_related_articles_exclude_current_and_other_categories(self):
        peer = Article.objects.create(
            title='Historia relacionada', slug='relacionada', summary='Resumen', body='Texto',
            author=self.author, published_at=timezone.now() - timedelta(hours=1),
        )
        peer.categories.add(self.category)
        other_category = Category.objects.create(name='Ciudades', slug='ciudades')
        other = Article.objects.create(
            title='Otra sección', slug='otra-seccion', summary='Resumen', body='Texto',
            author=self.author, published_at=timezone.now() - timedelta(hours=1),
        )
        other.categories.add(other_category)
        response = self.client.get(self.article.get_absolute_url())
        self.assertEqual(list(response.context['related_articles']), [peer])
        self.assertContains(response, peer.get_absolute_url())
        self.assertNotContains(response, other.title)

    def test_future_article_is_not_public(self):
        future = Article.objects.create(
            title='Noticia futura', slug='futura', summary='Futura', body='Cuerpo',
            author=self.author, published_at=timezone.now() + timedelta(days=1),
        )
        response = self.client.get(reverse('news:home'))
        self.assertNotIn(future, response.context['articles'])
        self.assertEqual(self.client.get(future.get_absolute_url()).status_code, 404)

    def test_home_empty_state(self):
        Article.objects.all().delete()
        self.assertContains(self.client.get(reverse('news:home')), 'Todavía no hay noticias.')

    def test_missing_article_and_category_return_404(self):
        self.assertEqual(self.client.get(reverse('news:detail', args=['inexistente'])).status_code, 404)
        self.assertEqual(self.client.get(reverse('news:category', args=['inexistente'])).status_code, 404)

    def test_editing_in_admin_updates_public_page(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('admin:news_article_change', args=[self.article.pk]), {
            'title': 'Título actualizado desde el panel', 'slug': self.article.slug,
            'summary': self.article.summary, 'body': self.article.body,
            'author': self.author.pk, 'categories': [self.category.pk],
            'published_at_0': '2025-01-01', 'published_at_1': '12:00:00', '_save': 'Guardar',
        })
        self.assertEqual(response.status_code, 302)
        self.assertContains(self.client.get(self.article.get_absolute_url()), 'Título actualizado desde el panel')

    def test_all_news_admin_pages_render(self):
        self.client.force_login(self.admin)
        for model in ('article', 'category', 'author'):
            with self.subTest(model=model):
                response = self.client.get(reverse(f'admin:news_{model}_changelist'))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'searchbar')

    def test_author_with_articles_cannot_be_deleted(self):
        with self.assertRaises(ProtectedError):
            self.author.delete()

    def test_stylesheet_is_discoverable(self):
        self.assertIsNotNone(finders.find('news/css/style.css'))


class SeedNewsTests(TestCase):
    def setUp(self):
        self.directory = self.enterContext(TemporaryDirectory())
        self.enterContext(override_settings(MEDIA_ROOT=self.directory))

    def test_seed_is_repeatable_preserves_edits_and_creates_images(self):
        call_command('seed_news', stdout=StringIO())
        self.assertEqual(Article.objects.count(), 6)
        self.assertEqual(Category.objects.count(), 3)
        self.assertTrue(get_user_model().objects.get(username='admin').is_superuser)
        for category in Category.objects.all():
            self.assertEqual(category.articles.count(), 2)
        for article in Article.objects.all():
            self.assertTrue(article.source_url.startswith('https://'))
            self.assertTrue(article.image_credit)
            self.assertEqual(article.author.name, 'Redacción Nexo')
        article = Article.objects.first()
        article.title = 'Cambio del editor'
        article.save()
        original_pks = list(Article.objects.order_by('pk').values_list('pk', flat=True))
        call_command('seed_news', stdout=StringIO())
        article.refresh_from_db()
        self.assertEqual(article.title, 'Cambio del editor')
        self.assertEqual(list(Article.objects.order_by('pk').values_list('pk', flat=True)), original_pks)
        for seeded_article in Article.objects.all():
            with seeded_article.featured_image.open('rb') as file:
                image = Image.open(file)
                self.assertGreaterEqual(image.width, 600)
                self.assertGreaterEqual(image.height, 300)
                self.assertEqual(image.format, 'JPEG')
                image.verify()

    def test_legacy_examples_are_converted_without_removing_user_content(self):
        from movies.models import Movie
        author = Author.objects.create(name='Autora anterior')
        old = Article.objects.create(
            title='Ejemplo anterior', slug='tecnologia-mirada-humana', summary='Ejemplo',
            body='Texto de prueba', author=author,
        )
        custom = Article.objects.create(
            title='Noticia del usuario', slug='noticia-del-usuario', summary='Resumen',
            body='Contenido del usuario', author=author,
        )
        movie = Movie.objects.create(title='Película existente', release_year=2020)
        call_command('seed_news', stdout=StringIO())
        old.refresh_from_db()
        self.assertEqual(old.slug, 'webb-primer-campo-profundo')
        self.assertTrue(old.source_url)
        self.assertTrue(Article.objects.filter(pk=custom.pk, body='Contenido del usuario').exists())
        self.assertTrue(Movie.objects.filter(pk=movie.pk).exists())
        self.assertEqual(Article.objects.count(), 7)
