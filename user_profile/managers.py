from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("Пользователь должен быть указан")

        if not email:
            raise ValueError("Адрес электронной почты должен быть указан")

        if not password:
            raise ValueError("Пароль должен быть указан")

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")

        return self.create_user(
            username,
            email,
            password,
            **extra_fields
        )

