from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from news.data.stories import STORIES
from news.models import Article, Author, Category


class Command(BaseCommand):
    help = 'Carga seis noticias reales con fuentes e imágenes; convierte los ejemplos anteriores.'

    @transaction.atomic
    def handle(self, *args, **options):
        image_root = Path(settings.BASE_DIR) / 'news' / 'data' / 'images'
        missing = [story['slug'] for story in STORIES if not (image_root / f"{story['slug']}.jpg").exists()]
        if missing:
            raise CommandError('Faltan imágenes reales. Ejecuta primero: python manage.py fetch_news_images')

        categories = {}
        for name, slug, description in [
            ('Tecnología', 'tecnologia', 'Ciencia y herramientas que amplían lo que podemos hacer.'),
            ('Cultura', 'cultura', 'Libros, patrimonio y acontecimientos culturales.'),
            ('Ciudades', 'ciudades', 'Movilidad, desarrollo urbano y vida en comunidad.'),
        ]:
            categories[slug], _ = Category.objects.get_or_create(
                slug=slug, defaults={'name': name, 'description': description},
            )
        author, _ = Author.objects.get_or_create(name='Redacción Nexo', defaults={
            'biography': 'Resúmenes propios en español basados en fuentes oficiales. Cada noticia enlaza su publicación original.',
        })

        created_count = converted_count = 0
        for story in STORIES:
            article = Article.objects.filter(slug=story['slug']).first()
            if article is None:
                article = Article.objects.filter(slug=story['legacy_slug']).first()
                if article is None:
                    article = Article()
                    created_count += 1
                else:
                    converted_count += 1
                article.title = story['title']
                article.slug = story['slug']
                article.summary = story['summary']
                article.body = story['body']
                article.author = author
                # Las fuentes indican el día, no la hora; el mediodía UTC conserva
                # ese día en la zona America/Lima usada por el portal.
                article.published_at = datetime.fromisoformat(story['date']).replace(hour=12, tzinfo=timezone.utc)
                article.source_name = story['source_name']
                article.source_url = story['source_url']
                article.image_credit = story['image_credit']
                article.image_source_url = story['image_url']
                with (image_root / f"{story['slug']}.jpg").open('rb') as image_file:
                    article.featured_image.save(f"{story['slug']}.jpg", File(image_file), save=False)
                article.save()
                article.categories.set([categories[story['category']]])
            elif not article.featured_image or not article.featured_image.storage.exists(article.featured_image.name):
                with (image_root / f"{story['slug']}.jpg").open('rb') as image_file:
                    article.featured_image.save(f"{story['slug']}.jpg", File(image_file), save=True)

        user, created = get_user_model().objects.get_or_create(username='admin', defaults={
            'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True,
        })
        if created:
            user.set_password('Admin12345')
            user.save()
            self.stdout.write('Superusuario local creado: admin / Admin12345')
        else:
            self.stdout.write('Usuario admin existente: se conservan su contraseña y permisos.')
        self.stdout.write(self.style.SUCCESS(f'Noticias nuevas: {created_count}. Ejemplos convertidos: {converted_count}.'))
        self.stdout.write('Seis noticias reales disponibles en /noticias/.')
