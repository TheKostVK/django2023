from django.urls import path

from .views import feedback, feedback_thank_you

urlpatterns = [
    path('', feedback, name='feedback'),
    path('thank_you/', feedback_thank_you, name='feedback_thank_you'),

]
