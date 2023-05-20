from django.db import models

from django.db import models


class News(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    image = models.ImageField(upload_to='news_images/')
    blog = models.CharField(max_length=200)
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
