from django.contrib import admin

from .models import Article, Author, Category


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'source_name', 'published_at', 'updated_at')
    list_filter = ('categories', 'author', 'source_name', 'published_at')
    search_fields = ('title', 'summary', 'body', 'author__name')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'published_at'
    list_select_related = ('author',)
    fieldsets = (
        ('Contenido', {'fields': ('title', 'slug', 'summary', 'body', 'featured_image')}),
        ('Publicación', {'fields': ('author', 'categories', 'published_at')}),
        ('Fuentes y créditos', {'fields': ('source_name', 'source_url', 'image_credit', 'image_source_url')}),
        ('Auditoría', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    list_filter = ('name',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'biography')
    list_filter = ('name',)
    search_fields = ('name', 'biography')
