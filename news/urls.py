# urls.py (внутри вашего приложения)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('create_news/', views.create_news, name='create_news'),
    path('edit_news/<int:news_id>/', views.edit_news, name='edit_news'),
]
