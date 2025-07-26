from rest_framework import serializers
from .models import BlogSource, Post


class BlogSourceSerializer(serializers.ModelSerializer):
    posts_count = serializers.ReadOnlyField()
    
    class Meta:
        model = BlogSource
        fields = [
            'id', 'name', 'description', 'homepage_url', 
            'logo_url', 'posts_count', 'created_at'
        ]


class PostSerializer(serializers.ModelSerializer):
    blog_source = BlogSourceSerializer(read_only=True)
    short_excerpt = serializers.ReadOnlyField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'link', 'excerpt', 'short_excerpt',
            'thumbnail_url', 'published_date', 'blog_source', 'created_at'
        ]