from rest_framework import serializers
from .models import BlogSource, Post, Category, MyPost


class CategorySerializer(serializers.ModelSerializer):
    posts_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'color', 
            'icon', 'posts_count', 'created_at'
        ]


class BlogSourceSerializer(serializers.ModelSerializer):
    posts_count = serializers.ReadOnlyField()
    tag_list = serializers.ReadOnlyField()
    
    class Meta:
        model = BlogSource
        fields = [
            'id', 'name', 'description', 'homepage_url', 'logo_url',
            'author', 'language', 'tags', 'tag_list', 'posts_count', 'created_at'
        ]


class PostSerializer(serializers.ModelSerializer):
    blog_source = BlogSourceSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    short_excerpt = serializers.ReadOnlyField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'link', 'excerpt', 'short_excerpt',
            'thumbnail_url', 'published_date', 'blog_source', 
            'category', 'created_at'
        ]


class MyPostSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    author = serializers.CharField(source='author.username', read_only=True)
    short_excerpt = serializers.ReadOnlyField()
    tag_list = serializers.ReadOnlyField()
    reading_time = serializers.ReadOnlyField()
    
    class Meta:
        model = MyPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'short_excerpt',
            'thumbnail_url', 'category', 'author', 'published_date',
            'views_count', 'tags', 'tag_list', 'reading_time', 'created_at'
        ]