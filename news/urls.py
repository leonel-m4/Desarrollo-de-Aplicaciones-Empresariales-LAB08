from django.urls import path

from . import views

app_name = 'news'

urlpatterns = [
    path('', views.home, name='home'),
    path('articulo/<slug:slug>/', views.detail, name='detail'),
    path('categoria/<slug:slug>/', views.category, name='category'),
]
