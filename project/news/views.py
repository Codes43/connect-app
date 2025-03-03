from rest_framework import generics
from .models import NewsArticle
from .serializers import NewsArticleSerializer


class NewsArticleListView(generics.ListCreateAPIView):
    queryset = NewsArticle.objects.order_by('?')
    serializer_class = NewsArticleSerializer


class NewsArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer
