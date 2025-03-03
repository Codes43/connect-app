from django.urls import path, include
from tastypie.api import Api
from .resources import NewsResource
from .views import NewsArticleListView, NewsArticleDetailView

v1_api = Api(api_name='v1')
v1_api.register(NewsResource())

urlpatterns = [
    path('api/', include(v1_api.urls)),
    path('articles/', NewsArticleListView.as_view(),
         name='news_article_list_create'),
    path('articles/<int:pk>/', NewsArticleDetailView.as_view(),
         name='news_article_detail')
]
