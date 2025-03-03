from rest_framework import serializers
from .models import NewsArticle


class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = '__all__'

    def get_author(self, obj):
        author = obj.author.capitalize()
        return self.get_author
