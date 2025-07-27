from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'blog-sources', views.BlogSourceViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'my-posts', views.MyPostViewSet)

app_name = 'aggregator'

urlpatterns = [
    # Frontend views
    path('', views.index, name='index'),  # New homepage
    path('all/', views.all_posts, name='all_posts'),  # Masonry layout page
    path('load-more/', views.load_more_posts, name='load_more_posts'),
    path('blog-sources/', views.blog_sources_list, name='blog_sources'),
    path('categories/', views.categories_list, name='categories'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('post/<slug:slug>/', views.my_post_detail, name='my_post_detail'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/stats/', views.stats_api, name='stats_api'),
]