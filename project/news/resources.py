from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from .models import News
from bs4 import BeautifulSoup
import requests


class NewsResource(ModelResource):
    class Meta:
        queryset = News.objects.all()
        resource_name = 'news'
        authentication = Authentication()
        authorization = Authorization()

    def get_object_list(self, request):
        response = requests.get("https://www.bbc.com/news")
        soup = BeautifulSoup(response.text, "html.parser")
        news = soup.select(".sc-93223220-0")

        for new in news:
            headline = new.select_one(".sc-8ea7699c-3").getText()
            try:
                title = (new.select_one(".sc-f98732b0-0") or new.select_one(
                    ".sc-e5949eb5-0") or new.select_one(".sc-b8778340-4")).getText()
            except AttributeError:
                title = None

            try:
                image_element = new.select_one(".sc-a34861b-1")
                img_tag = image_element.find_all("img")
                img_url = img_tag[1]
                img_src = img_url["src"]

            except AttributeError:
                img_tag = None

            try:
                location = new.select_one(".sc-6fba5bd4-2").getText()
            except AttributeError:
                location = "BBC NEWS"

            try:
                time = new.select_one(".sc-6fba5bd4-1").getText()
            except AttributeError:
                time = None

               # Check if news article already exists
            if not News.objects.filter(headline=headline).exists():
                News.objects.create(
                    headline=headline, title=title, location=location, time=time, image=img_src)

        return News.objects.all()
