from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Count
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import BlogSource, Post
from .serializers import BlogSourceSerializer, PostSerializer


def index(request):
    """Trang chính hiển thị danh sách bài viết"""
    # Get filter parameters
    blog_source_id = request.GET.get('blog_source')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    posts = Post.objects.select_related('blog_source').all()
    
    # Apply filters
    if blog_source_id:
        posts = posts.filter(blog_source_id=blog_source_id)
    
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(excerpt__icontains=search_query)
        )
    
    # Pagination for masonry layout - more items per page
    paginator = Paginator(posts, 30)  # Increased from 20 to 30
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get all blog sources for filter dropdown
    blog_sources = BlogSource.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_obj': page_obj,
        'blog_sources': blog_sources,
        'current_blog_source': blog_source_id,
        'search_query': search_query,
    }
    
    return render(request, 'aggregator/index.html', context)


def load_more_posts(request):
    """HTMX endpoint để tải thêm bài viết cho infinity scroll"""
    page_number = request.GET.get('page', 1)
    blog_source_id = request.GET.get('blog_source')
    search_query = request.GET.get('search', '')
    
    # Same filtering logic as index
    posts = Post.objects.select_related('blog_source').all()
    
    if blog_source_id:
        posts = posts.filter(blog_source_id=blog_source_id)
    
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(excerpt__icontains=search_query)
        )
    
    # Use same pagination size as index
    paginator = Paginator(posts, 30)
    page_obj = paginator.get_page(page_number)
    
    # For infinity scroll, return empty if no more pages
    if not page_obj.has_next() and page_number != '1' and not page_obj.object_list:
        return render(request, 'aggregator/partials/empty.html')
    
    return render(request, 'aggregator/partials/post_list.html', {
        'page_obj': page_obj
    })


def blog_sources_list(request):
    """Trang danh sách các blog nguồn"""
    blog_sources = BlogSource.objects.filter(is_active=True).order_by('name')
    
    return render(request, 'aggregator/blog_sources.html', {
        'blog_sources': blog_sources
    })


# REST API ViewSets
class BlogSourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BlogSource.objects.filter(is_active=True)
    serializer_class = BlogSourceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.select_related('blog_source').all()
    serializer_class = PostSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'excerpt']
    ordering_fields = ['published_date', 'created_at']
    ordering = ['-published_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        blog_source_id = self.request.query_params.get('blog_source')
        
        if blog_source_id:
            queryset = queryset.filter(blog_source_id=blog_source_id)
            
        return queryset


@api_view(['GET'])
def stats_api(request):
    """API endpoint để lấy thống kê"""
    total_posts = Post.objects.count()
    total_sources = BlogSource.objects.filter(is_active=True).count()
    
    # Top 5 blog sources by post count
    top_sources = BlogSource.objects.filter(is_active=True).annotate(
        posts_count=Count('posts')
    ).order_by('-posts_count')[:5]
    
    stats = {
        'total_posts': total_posts,
        'total_sources': total_sources,
        'top_sources': [
            {
                'name': source.name,
                'posts_count': source.posts_count,
                'id': source.id
            }
            for source in top_sources
        ]
    }
    
    return Response(stats)
