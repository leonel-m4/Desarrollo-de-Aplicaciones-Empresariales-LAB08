from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    name = models.CharField('nombre', max_length=80, unique=True)
    slug = models.SlugField('identificador', unique=True)
    description = models.TextField('descripción', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('news:category', kwargs={'slug': self.slug})


class Author(models.Model):
    name = models.CharField('nombre', max_length=120)
    biography = models.TextField('biografía', blank=True)
    photo = models.ImageField('fotografía', upload_to='news/authors/', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'autor'
        verbose_name_plural = 'autores'

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField('título', max_length=180)
    slug = models.SlugField('identificador', unique=True, max_length=180)
    summary = models.TextField('resumen', max_length=600)
    body = models.TextField('cuerpo')
    featured_image = models.ImageField('imagen destacada', upload_to='news/articles/', blank=True)
    source_name = models.CharField('fuente', max_length=120, blank=True)
    source_url = models.URLField('enlace a la fuente', max_length=1000, blank=True)
    image_credit = models.CharField('crédito de imagen', max_length=250, blank=True)
    image_source_url = models.URLField('origen de la imagen', max_length=1000, blank=True)
    published_at = models.DateTimeField('fecha de publicación', default=timezone.now)
    author = models.ForeignKey(Author, verbose_name='autor', related_name='articles', on_delete=models.PROTECT)
    categories = models.ManyToManyField(Category, verbose_name='categorías', related_name='articles')
    created_at = models.DateTimeField('fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('última modificación', auto_now=True)

    class Meta:
        ordering = ['-published_at', '-pk']
        verbose_name = 'noticia'
        verbose_name_plural = 'noticias'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:detail', kwargs={'slug': self.slug})
