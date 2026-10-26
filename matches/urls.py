from django.urls import path

from . import views

urlpatterns = [
    path('matches/', views.match_list, name='match_list'),
    # Маршрут статистики должен быть объявлен ДО маршрута со slug,
    # иначе слово «statistics» будет воспринято как slug матча.
    path('matches/statistics/', views.statistics, name='statistics'),
    path('matches/<slug:slug>/', views.match_detail, name='match_detail'),
]