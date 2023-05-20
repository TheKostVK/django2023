# views.py
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import News


def login(request):
    if request.method == 'POST':
        # Обработка логина пользователя
        username = request.POST['username']
        password = request.POST['password']

        # Проверка логина и пароля
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Успешная аутентификация
            login(request, user)
            return redirect('index')
        else:
            # Неверные учетные данные
            error_message = 'Неверное имя пользователя или пароль'
            return render(request, 'auth/login.html', {'error_message': error_message})

    return render(request, 'auth/login.html')


def register(request):
    if request.method == 'POST':
        # Обработка регистрации пользователя
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            # Проверка, что пароли совпадают
            try:
                # Проверка, что пользователь с таким именем уже не существует
                existing_user = User.objects.get(username=username)
                error_message = 'Пользователь с таким именем уже существует'
                return render(request, 'auth/register.html', {'error_message': error_message})
            except User.DoesNotExist:
                # Создание нового пользователя
                user = User.objects.create_user(username=username, password=password)
                user.save()
                return redirect('login')
        else:
            # Обработка случая, когда пароли не совпадают
            error_message = 'Пароли не совпадают'
            return render(request, 'auth/register.html', {'error_message': error_message})
    return render(request, 'auth/register.html')


def index(request):
    latest_news = News.objects.order_by('-published_date')[:5]
    return render(request, 'index.html', {'latest_news': latest_news})


@login_required
def create_news(request):
    if request.method == 'POST':
        # Получение данных из запроса
        title = request.POST['title']
        text = request.POST['text']
        image = request.FILES['image']
        blog = request.POST['blog']

        # Создание новости
        news = News(title=title, text=text, image=image, blog=blog)
        news.save()

        return redirect('index')
    return render(request, 'news/create_news.html')


@login_required
def edit_news(request, news_id):
    news = News.objects.get(id=news_id)
    if request.method == 'POST':
        # Получение данных из запроса
        title = request.POST['title']
        text = request.POST['text']

        # Редактирование новости
        news.title = title
        news.text = text
        # Save the changes to the news object
        news.save()

        return redirect('index')
    return render(request, 'news/edit_news.html', {'news': news})


def blog(request):
    blog_news = News.objects.filter(blog__isnull=False)
    return render(request, 'blog.html', {'blog_news': blog_news})
