from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Count, F
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import BlogSource, Post, Category, MyPost
from .serializers import BlogSourceSerializer, PostSerializer, CategorySerializer, MyPostSerializer


def index(request):
    """Homepage với layout mixed như trang tin tức"""
    # Featured posts (MyPost)
    featured_posts = MyPost.objects.filter(
        is_published=True, 
        is_featured=True
    ).select_related('category', 'author')[:3]
    
    # Latest posts from external blogs
    latest_external = Post.objects.select_related('blog_source', 'category').filter(
        blog_source__is_active=True
    )[:6]
    
    # Latest my posts
    latest_my_posts = MyPost.objects.filter(
        is_published=True
    ).select_related('category', 'author')[:4]
    
    # Popular categories (by post count)
    popular_categories = Category.objects.filter(
        is_active=True
    ).annotate(
        total_posts=Count('posts') + Count('my_posts')
    ).order_by('-total_posts')[:6]
    
    # Recent blog sources
    recent_sources = BlogSource.objects.filter(
        is_active=True
    ).order_by('-last_fetched')[:8]
    
    # Trending posts (last 7 days with most views for MyPost)
    week_ago = timezone.now() - timedelta(days=7)
    trending_posts = MyPost.objects.filter(
        is_published=True,
        published_date__gte=week_ago
    ).order_by('-views_count')[:5]
    
    context = {
        'featured_posts': featured_posts,
        'latest_external': latest_external,
        'latest_my_posts': latest_my_posts,
        'popular_categories': popular_categories,
        'recent_sources': recent_sources,
        'trending_posts': trending_posts,
    }
    
    return render(request, 'aggregator/index.html', context)


def all_posts(request):
    """Trang tất cả bài viết với masonry layout + infinity scroll"""
    # Get filter parameters
    blog_source_id = request.GET.get('blog_source')
    category_id = request.GET.get('category')
    search_query = request.GET.get('search', '')
    post_type = request.GET.get('type', 'all')  # all, external, my
    
    # Combine posts from both models
    all_posts_list = []
    
    if post_type in ['all', 'external']:
        # External posts
        external_posts = Post.objects.select_related('blog_source', 'category').filter(
            blog_source__is_active=True
        )
        
        if blog_source_id:
            external_posts = external_posts.filter(blog_source_id=blog_source_id)
        if category_id:
            external_posts = external_posts.filter(category_id=category_id)
        if search_query:
            external_posts = external_posts.filter(
                Q(title__icontains=search_query) | 
                Q(excerpt__icontains=search_query)
            )
        
        for post in external_posts:
            all_posts_list.append({
                'type': 'external',
                'object': post,
                'published_date': post.published_date,
            })
    
    if post_type in ['all', 'my']:
        # My posts
        my_posts = MyPost.objects.filter(is_published=True).select_related('category', 'author')
        
        if category_id:
            my_posts = my_posts.filter(category_id=category_id)
        if search_query:
            my_posts = my_posts.filter(
                Q(title__icontains=search_query) | 
                Q(excerpt__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        
        for post in my_posts:
            all_posts_list.append({
                'type': 'my',
                'object': post,
                'published_date': post.published_date or post.created_at,
            })
    
    # Sort by published date
    all_posts_list.sort(key=lambda x: x['published_date'], reverse=True)
    
    # Pagination for masonry layout
    paginator = Paginator(all_posts_list, 30)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    blog_sources = BlogSource.objects.filter(is_active=True).order_by('name')
    categories = Category.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_obj': page_obj,
        'blog_sources': blog_sources,
        'categories': categories,
        'current_blog_source': blog_source_id,
        'current_category': category_id,
        'current_type': post_type,
        'search_query': search_query,
    }
    
    return render(request, 'aggregator/all_posts.html', context)


def load_more_posts(request):
    """HTMX endpoint để tải thêm bài viết cho infinity scroll trong trang all"""
    # Reuse all_posts logic but return only the partial
    return all_posts(request)  # Will render the same template but HTMX will use partial


def blog_sources_list(request):
    """Trang danh sách blog sources theo alphabet như từ điển"""
    search = request.GET.get('search', '')
    letter = request.GET.get('letter', '')
    
    sources = BlogSource.objects.filter(is_active=True)
    
    if search:
        sources = sources.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(author__icontains=search)
        )
    
    if letter:
        sources = sources.filter(name__istartswith=letter)
    
    sources = sources.order_by('name')
    
    # Group by first letter
    grouped_sources = {}
    for source in sources:
        first_letter = source.name[0].upper()
        if first_letter not in grouped_sources:
            grouped_sources[first_letter] = []
        grouped_sources[first_letter].append(source)
    
    # Get alphabet letters that have sources
    available_letters = sorted(grouped_sources.keys())
    
    context = {
        'grouped_sources': grouped_sources,
        'available_letters': available_letters,
        'search_query': search,
        'current_letter': letter,
    }
    
    return render(request, 'aggregator/blog_sources.html', context)


def category_detail(request, slug):
    """Chi tiết category với posts thuộc category đó"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Get all posts in this category
    all_posts_list = []
    
    # External posts
    external_posts = category.posts.filter(blog_source__is_active=True)
    for post in external_posts:
        all_posts_list.append({
            'type': 'external',
            'object': post,
            'published_date': post.published_date,
        })
    
    # My posts
    my_posts = category.my_posts.filter(is_published=True)
    for post in my_posts:
        all_posts_list.append({
            'type': 'my',
            'object': post,
            'published_date': post.published_date or post.created_at,
        })
    
    # Sort by published date
    all_posts_list.sort(key=lambda x: x['published_date'], reverse=True)
    
    # Pagination
    paginator = Paginator(all_posts_list, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    
    return render(request, 'aggregator/category_detail.html', context)


def my_post_detail(request, slug):
    """Chi tiết bài viết của website"""
    post = get_object_or_404(MyPost, slug=slug, is_published=True)
    
    # Increase view count
    MyPost.objects.filter(id=post.id).update(views_count=F('views_count') + 1)
    post.refresh_from_db()
    
    # Related posts (same category)
    related_posts = MyPost.objects.filter(
        category=post.category,
        is_published=True
    ).exclude(id=post.id)[:4]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    
    return render(request, 'aggregator/my_post_detail.html', context)


def categories_list(request):
    """Danh sách tất cả categories"""
    categories = Category.objects.filter(is_active=True).annotate(
        total_posts=Count('posts') + Count('my_posts')
    ).order_by('-total_posts')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'aggregator/categories.html', context)


# REST API ViewSets
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class BlogSourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BlogSource.objects.filter(is_active=True)
    serializer_class = BlogSourceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'author']


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.select_related('blog_source', 'category').filter(blog_source__is_active=True)
    serializer_class = PostSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'excerpt']
    ordering_fields = ['published_date', 'created_at']
    ordering = ['-published_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        blog_source_id = self.request.query_params.get('blog_source')
        category_id = self.request.query_params.get('category')
        
        if blog_source_id:
            queryset = queryset.filter(blog_source_id=blog_source_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        return queryset


class MyPostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MyPost.objects.filter(is_published=True).select_related('category', 'author')
    serializer_class = MyPostSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['published_date', 'created_at', 'views_count']
    ordering = ['-published_date']


@api_view(['GET'])
def stats_api(request):
    """API endpoint để lấy thống kê"""
    total_external_posts = Post.objects.filter(blog_source__is_active=True).count()
    total_my_posts = MyPost.objects.filter(is_published=True).count()
    total_sources = BlogSource.objects.filter(is_active=True).count()
    total_categories = Category.objects.filter(is_active=True).count()
    
    stats = {
        'total_external_posts': total_external_posts,
        'total_my_posts': total_my_posts,
        'total_posts': total_external_posts + total_my_posts,
        'total_sources': total_sources,
        'total_categories': total_categories,
    }
    
    return Response(stats)
