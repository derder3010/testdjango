from django.db import models
from django.utils import timezone


class BlogSource(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tên blog")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    rss_url = models.URLField(verbose_name="RSS URL")
    homepage_url = models.URLField(blank=True, verbose_name="Trang chủ")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_fetched = models.DateTimeField(null=True, blank=True, verbose_name="Lần crawl cuối")
    logo_url = models.URLField(blank=True, verbose_name="Logo URL")

    class Meta:
        verbose_name = "Nguồn Blog"
        verbose_name_plural = "Nguồn Blog"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def posts_count(self):
        return self.posts.count()


class Post(models.Model):
    title = models.CharField(max_length=500, verbose_name="Tiêu đề")
    link = models.URLField(unique=True, verbose_name="Link gốc")
    excerpt = models.TextField(blank=True, verbose_name="Mô tả ngắn")
    thumbnail_url = models.URLField(blank=True, verbose_name="Ảnh thumbnail")
    published_date = models.DateTimeField(verbose_name="Ngày đăng")
    blog_source = models.ForeignKey(
        BlogSource, 
        on_delete=models.CASCADE, 
        related_name='posts',
        verbose_name="Nguồn blog"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bài viết"
        verbose_name_plural = "Bài viết"
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    @property
    def short_excerpt(self):
        if self.excerpt and len(self.excerpt) > 150:
            return self.excerpt[:150] + "..."
        return self.excerpt or ""
