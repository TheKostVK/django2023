from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

from .decorators import (  # Импорт пользовательских декораторов
    not_logged_in_required
)
from .forms import (  # Импорт форм
    UserRegistrationForm,
    LoginForm,
    UserProfileUpdateForm,
    ProfilePictureUpdateForm
)
from .models import Follow, User  # Импорт моделей


@never_cache
@not_logged_in_required  # Декоратор, требующий, чтобы пользователь не был авторизован для доступа к представлению
def login_user(request):
    form = LoginForm()  # Создание экземпляра формы входа

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )
            if user:
                login(request, user)  # Авторизация пользователя
                return redirect('home')
            else:
                messages.warning(request, "Неверные учетные данные")  # Сообщение об ошибке

    context = {
        "form": form  # Передача формы в контекст шаблона
    }
    return render(request, 'logReg/login.html', context)  # Рендеринг шаблона для страницы входа


def logout_user(request):
    logout(request)  # Выход пользователя из системы
    return redirect('login')  # Перенаправление на страницу входа


@never_cache
@not_logged_in_required
def register_user(request):
    form = UserRegistrationForm()  # Создание экземпляра формы регистрации пользователя

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))  # Установка пароля
            user.save()
            messages.success(request, "Регистрация успешна")  # Сообщение об успешной регистрации
            return redirect('login')

    context = {
        "form": form
    }
    return render(request, 'logReg/registration.html', context)


@login_required(login_url='login')  # Декоратор, требующий, чтобы пользователь был авторизован
def profile(request):
    account = get_object_or_404(User, pk=request.user.pk)  # Получение учетной записи пользователя
    form = UserProfileUpdateForm(instance=account)  # Создание экземпляра формы обновления профиля

    if request.method == "POST":
        if request.user.pk != account.pk:
            return redirect('home')

        form = UserProfileUpdateForm(request.POST, instance=account)
        if form.is_valid():
            form.save()  # Сохранение данных формы
            messages.success(request, "Профиль успешно обновлен")  # Сообщение об успешном обновлении профиля
            return redirect('profile')
        else:
            print(form.errors)

    context = {
        "account": account,
        "form": form
    }
    return render(request, 'profile/profile.html', context)


@login_required
def change_profile_picture(request):
    if request.method == "POST":

        form = ProfilePictureUpdateForm(request.POST, request.FILES)

        if form.is_valid():
            image = request.FILES['profile_image']
            user = get_object_or_404(User, pk=request.user.pk)

            if request.user.pk != user.pk:
                return redirect('home')

            user.profile_image = image  # Обновление изображения профиля
            user.save()
            messages.success(request, "Изображение профиля успешно обновлено")  # Сообщение об успешном обновлении изображения профиля

        else:
            print(form.errors)

    return redirect('profile')


def view_user_information(request, username):
    account = get_object_or_404(User, username=username)  # Получение учетной записи пользователя
    following = False
    muted = None

    if request.user.is_authenticated:

        if request.user.id == account.id:
            return redirect("profile")

        followers = account.followers.filter(
            followed_by__id=request.user.id
        )
        if followers.exists():
            following = True

    if following:
        queryset = followers.first()
        if queryset.muted:
            muted = True
        else:
            muted = False

    context = {
        "account": account,
        "following": following,
        "muted": muted
    }
    return render(request, "profile/user_information.html", context)


@login_required(login_url="login")
def follow_or_unfollow_user(request, user_id):
    followed = get_object_or_404(User, id=user_id)
    followed_by = get_object_or_404(User, id=request.user.id)

    follow, created = Follow.objects.get_or_create(
        followed=followed,
        followed_by=followed_by
    )

    if created:
        followed.followers.add(follow)

    else:
        followed.followers.remove(follow)
        follow.delete()

    return redirect("view_user_information", username=followed.username)


@login_required(login_url='login')
def mute_or_unmute_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    follower = get_object_or_404(User, pk=request.user.pk)
    instance = get_object_or_404(
        Follow,
        followed=user,
        followed_by=follower
    )

    if instance.muted:
        instance.muted = False
        instance.save()

    else:
        instance.muted = True
        instance.save()

    return redirect('view_user_information', username=user.username)
