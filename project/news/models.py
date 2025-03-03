from django.db import models

# Create your models here.
from django.db import models
from django.forms import DateTimeField
from tastypie.resources import ModelResource
# Create your models here.


class News(models.Model):
    headline = models.CharField(max_length=255)
    title = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, default="BBC NEWS")
    time = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.headline


class NewsArticle(models.Model):
    title = models.CharField(max_length=255)
    content = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(null=True)
    published_date = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=255)

    def __str__(self):
        return self.title
