from django.contrib import admin
from .models import BlogSource, Post, Category, MyPost


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'posts_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'posts_count']
    list_editable = ['is_active', 'color']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Hiển thị', {
            'fields': ('color', 'icon', 'is_active')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at', 'posts_count'),
            'classes': ('collapse',)
        })
    )


@admin.register(BlogSource)
class BlogSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'language', 'rss_url', 'is_active', 'posts_count', 'last_fetched']
    list_filter = ['is_active', 'language', 'created_at', 'last_fetched']
    search_fields = ['name', 'description', 'author']
    readonly_fields = ['created_at', 'updated_at', 'last_fetched', 'posts_count']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'author', 'description', 'homepage_url', 'logo_url')
        }),
        ('RSS Settings', {
            'fields': ('rss_url', 'is_active', 'language')
        }),
        ('Tags và phân loại', {
            'fields': ('tags',),
            'description': 'Phân cách bằng dấu phẩy'
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at', 'updated_at', 'last_fetched'),
            'classes': ('collapse',)
        })
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'blog_source', 'category', 'published_date', 'created_at']
    list_filter = ['blog_source', 'category', 'published_date', 'created_at']
    search_fields = ['title', 'excerpt']
    readonly_fields = ['created_at']
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Thông tin bài viết', {
            'fields': ('title', 'link', 'excerpt', 'thumbnail_url')
        }),
        ('Phân loại', {
            'fields': ('category',)
        }),
        ('Metadata', {
            'fields': ('blog_source', 'published_date', 'created_at'),
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('blog_source', 'category')


@admin.register(MyPost)
class MyPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'is_featured', 'published_date', 'views_count']
    list_filter = ['is_published', 'is_featured', 'category', 'author', 'published_date']
    search_fields = ['title', 'content', 'excerpt']
    readonly_fields = ['created_at', 'updated_at', 'views_count', 'reading_time']
    list_editable = ['is_published', 'is_featured']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Thông tin bài viết', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'thumbnail_url')
        }),
        ('Phân loại', {
            'fields': ('category', 'tags'),
            'description': 'Tags phân cách bằng dấu phẩy'
        }),
        ('Xuất bản', {
            'fields': ('author', 'is_published', 'is_featured', 'published_date')
        }),
        ('Thống kê', {
            'fields': ('views_count', 'reading_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.author = request.user
        super().save_model(request, obj, form, change)
