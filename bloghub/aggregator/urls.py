from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'blog-sources', views.BlogSourceViewSet)
router.register(r'posts', views.PostViewSet)

app_name = 'aggregator'

urlpatterns = [
    # Frontend views
    path('', views.index, name='index'),
    path('load-more/', views.load_more_posts, name='load_more_posts'),
    path('blog-sources/', views.blog_sources_list, name='blog_sources'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/stats/', views.stats_api, name='stats_api'),
]