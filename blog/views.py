from django.contrib import messages  # Импорт функции сообщений
from django.contrib.auth.decorators import login_required  # Декоратор, требующий аутентификации пользователя
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator  # Импорт классов для пагинации
from django.db.models import Q  # Импорт оператора Q для построения сложных запросов
from django.http import JsonResponse  # Импорт JsonResponse для отправки данных в формате JSON
from django.shortcuts import get_object_or_404, redirect, render  # Импорт функций для работы с объектами и рендеринга шаблонов
from django.utils.text import slugify  # Импорт функции slugify для создания URL-адресов

from user_profile.models import User  # Импорт моделей профиля пользователя
from .forms import TextForm, AddBlogForm  # Импорт форм
from .models import (  # Импорт моделей поста, категории, ответов, тегов и комментариев
    Blog,
    Category,
    Reply,
    Tag,
    Comment
)


# Функция для отображения домашней страницы
def home(request):
    blogs = Blog.objects.order_by('-created_date')  # Получение всех блогов, отсортированных по дате создания
    tags = Tag.objects.order_by('-created_date')  # Получение всех тегов, отсортированных по дате создания
    context = {
        "blogs": blogs,  # Передача блогов в контекст шаблона
        "tags": tags  # Передача тегов в контекст шаблона
    }
    return render(request, 'base/home.html', context)  # Рендеринг шаблона домашней страницы


# Функция для отображения страницы блогов
def blogs(request):
    queryset = Blog.objects.order_by('-created_date')  # Получение всех блогов, отсортированных по дате создания
    tags = Tag.objects.order_by('-created_date')  # Получение всех тегов, отсортированных по дате создания
    page = request.GET.get('page', 1)  # Получение номера текущей страницы из GET-запроса, по умолчанию - 1
    paginator = Paginator(queryset, 4)  # Создание объекта пагинатора для разбиения результатов на страницы

    try:
        blogs = paginator.page(page)  # Получение объекта Page с результатами для текущей страницы
    except EmptyPage:
        blogs = paginator.page(1)  # Если указанная страница пуста, показываем первую страницу
    except PageNotAnInteger:
        blogs = paginator.page(1)  # Если номер страницы не является целым числом, показываем первую страницу
        return redirect('blogs')  # Перенаправляем на страницу блогов

    context = {
        "blogs": blogs,  # Передача объекта Page с блогами в контекст шаблона
        "tags": tags,  # Передача всех тегов в контекст шаблона
        "paginator": paginator  # Передача объекта пагинатора в контекст шаблона
    }
    return render(request, 'blog/blogs.html', context)  # Рендеринг шаблона страницы блогов


# Функция для отображения страницы блогов определенной категории
def category_blogs(request, slug):
    category = get_object_or_404(Category, slug=slug)  # Получение объекта категории по слагу
    queryset = category.category_blogs.all()  # Получение всех блогов в указанной категории
    tags = Tag.objects.order_by('-created_date')[:5]  # Получение последних пяти тегов
    page = request.GET.get('page', 1)  # Получение номера текущей страницы из GET-запроса, по умолчанию - 1
    paginator = Paginator(queryset, 2)  # Создание объекта пагинатора для разбиения результатов на страницы
    all_blogs = Blog.objects.order_by('-created_date')[:5]  # Получение последних пяти блогов

    try:
        blogs = paginator.page(page)  # Получение объекта Page с результатами для текущей страницы
    except EmptyPage:
        blogs = paginator.page(1)  # Если указанная страница пуста, показываем первую страницу
    except PageNotAnInteger:
        blogs = paginator.page(1)  # Если номер страницы не является целым числом, показываем первую страницу
        return redirect('blogs')  # Перенаправляем на страницу блогов

    context = {
        "blogs": blogs,  # Передача объекта Page с блогами в контекст шаблона
        "tags": tags,  # Передача всех тегов в контекст шаблона
        "all_blogs": all_blogs  # Передача последних пяти блогов в контекст шаблона
    }
    return render(request, 'blog/category_blogs.html', context)  # Рендеринг шаблона страницы блогов категории


# Функция для отображения страницы блогов с указанным тегом
def tag_blogs(request, slug):
    tag = get_object_or_404(Tag, slug=slug)  # Получение объекта тега по слагу
    queryset = tag.tag_blogs.all()  # Получение всех блогов с указанным тегом
    tags = Tag.objects.order_by('-created_date')[:5]  # Получение последних пяти тегов
    page = request.GET.get('page', 1)  # Получение номера текущей страницы из GET-запроса, по умолчанию - 1
    paginator = Paginator(queryset, 2)  # Создание объекта пагинатора для разбиения результатов на страницы
    all_blogs = Blog.objects.order_by('-created_date')[:5]  # Получение последних пяти блогов

    try:
        blogs = paginator.page(page)  # Получение объекта Page с результатами для текущей страницы
    except EmptyPage:
        blogs = paginator.page(1)  # Если указанная страница пуста, показываем первую страницу
    except PageNotAnInteger:
        blogs = paginator.page(1)  # Если номер страницы не является целым числом, показываем первую страницу
        return redirect('blogs')  # Перенаправляем на страницу блогов

    context = {
        "blogs": blogs,  # Передача объекта Page с блогами в контекст шаблона
        "tags": tags,  # Передача всех тегов в контекст шаблона
        "all_blogs": all_blogs  # Передача последних пяти блогов в контекст шаблона
    }
    return render(request, 'blog/category_blogs.html', context)  # Рендеринг шаблона страницы блогов с тегом


# Функция для отображения подробностей поста
def blog_details(request, slug):
    form = TextForm()  # Создание формы комментария
    blog = get_object_or_404(Blog, slug=slug)  # Получение объекта поста по слагу
    category = Category.objects.get(id=blog.category.id)  # Получение объекта категории поста
    related_blogs = category.category_blogs.all()  # Получение всех блогов из той же категории
    tags = Tag.objects.order_by('-created_date')[:5]  # Получение последних пяти тегов
    liked_by = request.user in blog.likes.all()  # Проверка, поставил ли текущий пользователь лайк этому блогу

    if request.method == "POST" and request.user.is_authenticated:
        form = TextForm(request.POST)  # Создание формы с данными из POST-запроса
        if form.is_valid():  # Проверка валидности формы
            Comment.objects.create(  # Создание комментария
                user=request.user,  # Текущий пользователь
                blog=blog,  # Текущий пост
                text=form.cleaned_data.get('text')  # Текст комментария
            )
            return redirect('blog_details', slug=slug)  # Перенаправление на страницу с деталями поста

    context = {
        "blog": blog,  # Передача объекта поста в контекст шаблона
        "related_blogs": related_blogs,  # Передача связанных блогов в контекст шаблона
        "tags": tags,  # Передача всех тегов в контекст шаблона
        "form": form,  # Передача формы комментария в контекст шаблона
        "liked_by": liked_by  # Передача информации о лайке в контекст шаблона
    }
    return render(request, 'blog/blog_details.html', context)  # Рендеринг шаблона страницы с деталями поста


# Функция для добавления ответа на комментарий к блогу
@login_required(login_url='login')
def add_reply(request, blog_id, comment_id):
    blog = get_object_or_404(Blog, id=blog_id)  # Получение объекта поста по идентификатору
    if request.method == "POST":  # Проверка метода запроса
        form = TextForm(request.POST)  # Создание формы с данными из POST-запроса
        if form.is_valid():  # Проверка валидности формы
            comment = get_object_or_404(Comment, id=comment_id)  # Получение объекта комментария по идентификатору
            Reply.objects.create(  # Создание ответа на комментарий
                user=request.user,  # Текущий пользователь
                comment=comment,  # Текущий комментарий
                text=form.cleaned_data.get('text')  # Текст ответа
            )
    return redirect('blog_details', slug=blog.slug)  # Перенаправление на страницу с деталями поста


# Функция для установки или удаления лайка для поста
@login_required(login_url='login')
def like_blog(request, pk):
    context = {}
    blog = get_object_or_404(Blog, pk=pk)  # Получение объекта поста по идентификатору

    if request.user in blog.likes.all():  # Проверка, поставил ли текущий пользователь лайк этому блогу
        blog.likes.remove(request.user)  # Удаление лайка пользователя
        context['liked'] = False  # Установка флага liked в False
        context['like_count'] = blog.likes.all().count()  # Получение общего количества лайков

    else:
        blog.likes.add(request.user)  # Добавление лайка пользователя
        context['liked'] = True  # Установка флага liked в True
        context['like_count'] = blog.likes.all().count()  # Получение общего количества лайков

    return JsonResponse(context, safe=False)  # Возврат JSON-ответа


# Функция для поиска блогов по ключевому слову
def search_blogs(request):
    search_key = request.GET.get('search', None)  # Получение ключевого слова для поиска из GET-запроса
    recent_blogs = Blog.objects.order_by('-created_date')  # Получение всех блогов, отсортированных по дате создания
    tags = Tag.objects.order_by('-created_date')  # Получение всех тегов, отсортированных по дате создания

    if search_key:  # Проверка наличия ключевого слова
        blogs = Blog.objects.filter(  # Поиск блогов по ключевому слову
            Q(title__icontains=search_key) |  # Поиск по заголовку
            Q(category__title__icontains=search_key) |  # Поиск по категории
            Q(user__username__icontains=search_key) |  # Поиск по имени пользователя
            Q(tags__title__icontains=search_key)  # Поиск по тегам
        ).distinct()  # Удаление дубликатов из результатов

        context = {
            "blogs": blogs,  # Передача найденных блогов в контекст шаблона
            "recent_blogs": recent_blogs,  # Передача всех блогов в контекст шаблона
            "tags": tags,  # Передача всех тегов в контекст шаблона
            "search_key": search_key  # Передача ключевого слова в контекст шаблона
        }

        return render(request, 'base/search.html', context)  # Рендеринг шаблона страницы поиска

    else:
        return redirect('home')  # Перенаправление на домашнюю страницу


# Функция для отображения всех блогов пользователя
@login_required(login_url='login')
def my_blogs(request):
    queryset = request.user.user_blogs.all()  # Получение всех блогов пользователя
    page = request.GET.get('page', 1)  # Получение номера текущей страницы из GET-запроса, по умолчанию - 1
    paginator = Paginator(queryset, 6)  # Создание объекта пагинатора для разбиения результатов на страницы
    delete = request.GET.get('delete', None)  # Получение параметра delete из GET-запроса

    if delete:  # Проверка наличия параметра delete
        blog = get_object_or_404(Blog, pk=delete)  # Получение объекта поста по идентификатору

        if request.user.pk != blog.user.pk:  # Проверка, является ли текущий пользователь владельцем поста
            return redirect('home')  # Перенаправление на домашнюю страницу

        blog.delete()  # Удаление поста
        messages.success(request, "Ваш пост был удален!")  # Отправка сообщения об успешном удалении поста
        return redirect('my_blogs')  # Перенаправление на страницу всех блогов пользователя

    try:
        blogs = paginator.page(page)  # Получение объекта Page с результатами для текущей страницы
    except EmptyPage:
        blogs = paginator.page(1)  # Если указанная страница пуста, показываем первую страницу
    except PageNotAnInteger:
        blogs = paginator.page(1)  # Если номер страницы не является целым числом, показываем первую страницу
        return redirect('blogs')  # Перенаправляем на страницу блогов

    context = {
        "blogs": blogs,  # Передача объекта Page с блогами в контекст шаблона
        "paginator": paginator  # Передача объекта пагинатора в контекст шаблона
    }

    return render(request, 'blog/my_blogs.html', context)  # Рендеринг шаблона страницы всех блогов пользователя


# Функция для добавления нового поста
@login_required(login_url='login')
def add_blog(request):
    form = AddBlogForm()  # Создание формы для добавления поста

    if request.method == "POST":  # Проверка метода запроса
        form = AddBlogForm(request.POST,
                           request.FILES)  # Создание формы с данными из POST-запроса и загруженными файлами
        if form.is_valid():  # Проверка валидности формы
            tags = request.POST['tags'].split(',')  # Разделение строки тегов на список по запятым
            user = get_object_or_404(User, pk=request.user.pk)  # Получение объекта пользователя
            category = get_object_or_404(Category, pk=request.POST['category'])  # Получение объекта категории
            blog = form.save(commit=False)  # Сохранение формы, но без сохранения в базу данных
            blog.user = user  # Установка текущего пользователя в качестве автора поста
            blog.category = category  # Установка выбранной категории поста
            blog.save()  # Сохранение поста в базе данных

            for tag in tags:  # Перебор всех тегов
                tag_input = Tag.objects.filter(  # Проверка наличия тега в базе данных
                    title__iexact=tag.strip(),  # Сравнение без учета регистра
                    slug=slugify(tag.strip())  # Создание слага для тега
                )
                if tag_input.exists():  # Если тег уже существует
                    t = tag_input.first()  # Получаем первый найденный тег
                    blog.tags.add(t)  # Добавляем тег к блогу

                else:
                    if tag != '':  # Проверка наличия тега
                        new_tag = Tag.objects.create(  # Создание нового тега
                            title=tag.strip(),  # Установка названия тега
                            slug=slugify(tag.strip())  # Установка слага тега
                        )
                        blog.tags.add(new_tag)  # Добавляем новый тег к блогу

            messages.success(request, "Блог успешно добавлен")  # Отправка сообщения об успешном добавлении поста
            return redirect('blog_details', slug=blog.slug)  # Перенаправление на страницу с деталями поста
        else:
            print(form.errors)  # Вывод ошибок формы в консоль

    context = {
        "form": form  # Передача формы в контекст шаблона
    }
    return render(request, 'blog/add_blog.html', context)  # Рендеринг шаблона страницы добавления поста


# Функция для обновления существующего поста
@login_required(login_url='login')
def update_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug)  # Получение объекта поста по слагу
    form = AddBlogForm(instance=blog)  # Создание формы для обновления поста с данными из объекта поста

    if request.method == "POST":  # Проверка метода запроса
        form = AddBlogForm(request.POST, request.FILES, instance=blog)  # Создание формы с данными из POST-запроса
        if form.is_valid():  # Проверка валидности формы
            if request.user.pk != blog.user.pk:  # Проверка, является ли текущий пользователь автором поста
                return redirect('home')  # Перенаправление на домашнюю страницу

            tags = request.POST['tags'].split(',')  # Разделение строки тегов на список по запятым
            user = get_object_or_404(User, pk=request.user.pk)  # Получение объекта пользователя
            category = get_object_or_404(Category, pk=request.POST['category'])  # Получение объекта категории
            blog = form.save(commit=False)  # Сохранение формы, но без сохранения в базу данных
            blog.user = user  # Установка текущего пользователя в качестве автора поста
            blog.category = category  # Установка выбранной категории поста
            blog.save()  # Сохранение поста в базе данных

            for tag in tags:  # Перебор всех тегов
                tag_input = Tag.objects.filter(  # Проверка наличия тега в базе данных
                    title__iexact=tag.strip(),  # Сравнение без учета регистра
                    slug=slugify(tag.strip())  # Создание слага для тега
                )
                if tag_input.exists():  # Если тег уже существует
                    t = tag_input.first()  # Получаем первый найденный тег
                    blog.tags.add(t)  # Добавляем тег к блогу

                else:
                    if tag != '':  # Проверка наличия тега
                        new_tag = Tag.objects.create(  # Создание нового тега
                            title=tag.strip(),  # Установка названия тега
                            slug=slugify(tag.strip())  # Установка слага тега
                        )
                        blog.tags.add(new_tag)  # Добавляем новый тег к блогу

            messages.success(request, "Блог успешно обновлен")  # Отправка сообщения об успешном обновлении поста
            return redirect('blog_details', slug=blog.slug)  # Перенаправление на страницу с деталями поста
        else:
            print(form.errors)  # Вывод ошибок формы в консоль

    context = {
        "form": form,  # Передача формы в контекст шаблона
        "blog": blog  # Передача объекта поста в контекст шаблона
    }
    return render(request, 'blog/update_blog.html', context)  # Рендеринг шаблона страницы обновления поста
