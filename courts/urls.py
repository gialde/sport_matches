from django.urls import path
from . import views

urlpatterns = [
    path('courts/', views.court_list, name='court_list'),
]