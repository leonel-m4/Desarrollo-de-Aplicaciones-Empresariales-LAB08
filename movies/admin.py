from django.contrib import admin
from django.db.models import Avg

from .models import Genre, Movie, Person, Rating


class AuditReadOnlyMixin:
    readonly_fields = ('created_at', 'updated_at')


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 1
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Genre)
class GenreAdmin(AuditReadOnlyMixin, admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)


@admin.register(Person)
class PersonAdmin(AuditReadOnlyMixin, admin.ModelAdmin):
    list_display = ('name', 'birth_date', 'created_at', 'updated_at')
    search_fields = ('name',)


@admin.register(Movie)
class MovieAdmin(AuditReadOnlyMixin, admin.ModelAdmin):
    list_display = ('title', 'release_year', 'director', 'average_rating', 'created_at', 'updated_at')
    list_filter = ('genres', 'release_year')
    search_fields = ('title', 'director__name', 'cast__name')
    filter_horizontal = ('genres', 'cast')
    inlines = (RatingInline,)

    @admin.display(description='promedio')
    def average_rating(self, obj):
        average = obj.ratings.aggregate(value=Avg('score'))['value']
        return round(average, 2) if average is not None else '-'


@admin.register(Rating)
class RatingAdmin(AuditReadOnlyMixin, admin.ModelAdmin):
    list_display = ('movie', 'score', 'created_at', 'updated_at')
    list_filter = ('score', 'movie__genres', 'movie__release_year')
    search_fields = ('movie__title', 'comment')
