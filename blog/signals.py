from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from notification.models import Notification  # Импорт модели уведомлений
from user_profile.models import Follow, User  # Импорт моделей
from .models import Blog  # Импорт модели блога


@receiver(post_save, sender=Blog)  # Сигнал, вызываемый после сохранения объекта блога
def send_notification_to_followers_when_blog_created(instance, created, *args, **kwargs):
    if created:  # Проверка, был ли объект блога создан
        followers = instance.user.followers.all()  # Получение всех подписчиков пользователя блога

        for data in followers:
            follower = data.followed_by  # Получение пользователя-подписчика

            if not data.muted:  # Проверка, не отключены ли уведомления для данного подписчика
                Notification.objects.create(  # Создание уведомления
                    content_object=instance,
                    user=follower,
                    text=f"{instance.user.username} опубликовал(а) новый блог",
                    notification_types="Blog"
                )


@receiver(post_save, sender=Follow)  # Сигнал, вызываемый после сохранения объекта подписки
def send_notification_to_user_when_someone_followed(instance, created, *args, **kwargs):
    if created:  # Проверка, была ли подписка создана
        followed = instance.followed  # Получение пользователя, на которого была оформлена подписка

        if not instance.muted:  # Проверка, не отключены ли уведомления для данной подписки
            Notification.objects.create(  # Создание уведомления
                content_object=instance,
                user=followed,
                text=f"{instance.followed_by.username} начал(а) следить за вами",
                notification_types="Follow"
            )


@receiver(m2m_changed, sender=Blog.likes.through)  # Сигнал, вызываемый после изменения многие-ко-многим связи "лайков" блога
def send_notification_when_someone_likes_blog(instance, pk_set, action, *args, **kwargs):
    pk = list(pk_set)[0]  # Получение первичного ключа пользователя, который поставил лайк
    user = User.objects.get(pk=pk)  # Получение пользователя

    if action == "post_add":  # Проверка, был ли лайк добавлен
        Notification.objects.create(  # Создание уведомления
            content_object=instance,
            user=instance.user,
            text=f"{user.username} поставил(а) лайк вашему блогу",
            notification_types="Like"
        )
