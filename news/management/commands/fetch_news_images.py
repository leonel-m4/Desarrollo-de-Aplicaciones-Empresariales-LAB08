from io import BytesIO
from urllib.request import Request, urlopen

from PIL import Image, ImageOps, UnidentifiedImageError
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.management.base import BaseCommand, CommandError

from news.data.stories import STORIES


class Command(BaseCommand):
    help = 'Descarga y valida las seis imágenes reales del catálogo de noticias.'

    def handle(self, *args, **options):
        storage = FileSystemStorage(location=settings.BASE_DIR / 'news' / 'data' / 'images')
        for story in STORIES:
            name = f"{story['slug']}.jpg"
            if storage.exists(name):
                self.stdout.write(f'Ya disponible: {name}')
                continue
            try:
                request = Request(story['image_url'], headers={'User-Agent': 'Nexo-Lab/1.0'})
                with urlopen(request, timeout=30) as response:
                    data = response.read(20 * 1024 * 1024 + 1)
                if len(data) > 20 * 1024 * 1024:
                    raise ValueError('La imagen supera el límite de 20 MB.')
                with Image.open(BytesIO(data)) as image:
                    image.verify()
                with Image.open(BytesIO(data)) as image:
                    image = ImageOps.exif_transpose(image).convert('RGB')
                    image.thumbnail((1800, 1800))
                    output = BytesIO()
                    image.save(output, format='JPEG', quality=92)
                    width, height = image.size
                storage.save(name, ContentFile(output.getvalue()))
            except (OSError, ValueError, UnidentifiedImageError) as exc:
                raise CommandError(f"No se pudo descargar {story['title']}: {exc}") from exc
            self.stdout.write(self.style.SUCCESS(f'{name}: {width} x {height}'))
