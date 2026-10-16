from django.urls import path

from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalogo/', views.catalog, name='catalog'),
    path('peliculas/<int:pk>/recomendaciones/', views.movie_recommendations, name='recommendations'),
]
