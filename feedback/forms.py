from django import forms

from .models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'theme','message']
        labels = {
            'name': 'Имя',
            'email': 'Email',
            'theme': 'Тема обращения',
            'message': 'Сообщение',
        }
