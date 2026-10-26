"""Корневая конфигурация URL: здесь подключаются urls.py всех приложений."""

from django.urls import include, path

urlpatterns = [
    path('', include('homepage.urls')),
    path('', include('courts.urls')),
    path('', include('matches.urls')),
]