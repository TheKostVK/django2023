from django.shortcuts import render, redirect

from .forms import FeedbackForm


def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('feedback_thank_you')  # Перенаправление на страницу "спасибо" после успешной отправки формы
    else:
        form = FeedbackForm()
    return render(request, 'feedback/feedbackForm.html', {'form': form})


def feedback_thank_you(request):
    return render(request, 'feedback/feedbackEnd.html')
