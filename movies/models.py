from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Genre(models.Model):
    name = models.CharField('nombre', max_length=80, unique=True)
    created_at = models.DateTimeField('fecha de creacion', auto_now_add=True)
    updated_at = models.DateTimeField('ultima modificacion', auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'genero'
        verbose_name_plural = 'generos'

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField('nombre', max_length=120)
    biography = models.TextField('biografia', blank=True)
    birth_date = models.DateField('fecha de nacimiento', null=True, blank=True)
    created_at = models.DateTimeField('fecha de creacion', auto_now_add=True)
    updated_at = models.DateTimeField('ultima modificacion', auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'persona'
        verbose_name_plural = 'personas'

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField('titulo', max_length=150)
    synopsis = models.TextField('sinopsis', blank=True)
    release_year = models.PositiveIntegerField('anio de estreno')
    poster = models.ImageField('afiche', upload_to='movies/posters/', blank=True)
    poster_url = models.URLField('url del afiche', blank=True)
    genres = models.ManyToManyField(Genre, verbose_name='generos', related_name='movies')
    director = models.ForeignKey(
        Person,
        verbose_name='director',
        related_name='directed_movies',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    cast = models.ManyToManyField(Person, verbose_name='reparto', related_name='acted_movies', blank=True)
    created_at = models.DateTimeField('fecha de creacion', auto_now_add=True)
    updated_at = models.DateTimeField('ultima modificacion', auto_now=True)

    class Meta:
        ordering = ['-release_year', 'title']
        verbose_name = 'pelicula'
        verbose_name_plural = 'peliculas'

    def __str__(self):
        return f'{self.title} ({self.release_year})'


class Rating(models.Model):
    movie = models.ForeignKey(Movie, verbose_name='pelicula', related_name='ratings', on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField('puntuacion', validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField('comentario', blank=True)
    created_at = models.DateTimeField('fecha de creacion', auto_now_add=True)
    updated_at = models.DateTimeField('ultima modificacion', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'valoracion'
        verbose_name_plural = 'valoraciones'

    def __str__(self):
        return f'{self.movie} - {self.score}/5'
