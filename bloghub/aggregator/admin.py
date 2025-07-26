from django.contrib import admin
from .models import BlogSource, Post


@admin.register(BlogSource)
class BlogSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'rss_url', 'is_active', 'posts_count', 'last_fetched', 'created_at']
    list_filter = ['is_active', 'created_at', 'last_fetched']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'last_fetched', 'posts_count']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'description', 'homepage_url', 'logo_url')
        }),
        ('RSS Settings', {
            'fields': ('rss_url', 'is_active')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at', 'updated_at', 'last_fetched'),
            'classes': ('collapse',)
        })
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'blog_source', 'published_date', 'created_at']
    list_filter = ['blog_source', 'published_date', 'created_at']
    search_fields = ['title', 'excerpt']
    readonly_fields = ['created_at']
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Thông tin bài viết', {
            'fields': ('title', 'link', 'excerpt', 'thumbnail_url')
        }),
        ('Metadata', {
            'fields': ('blog_source', 'published_date', 'created_at'),
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('blog_source')
