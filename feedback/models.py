from django.db import models


class Feedback(models.Model):
    THEMES_CHOICES = [
        ('Technical', 'Технический вопрос'),
        ('General', 'Общий вопрос'),
        ('Bug', 'Сообщение об ошибке'),
        ('Other', 'Другое'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    theme = models.CharField(max_length=20, choices=THEMES_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
