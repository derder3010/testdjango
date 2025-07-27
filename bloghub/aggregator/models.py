from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên danh mục")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    color = models.CharField(max_length=7, default='#3B82F6', verbose_name="Màu sắc")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icon class")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('aggregator:category_detail', kwargs={'slug': self.slug})

    @property
    def posts_count(self):
        return self.posts.filter(blog_source__is_active=True).count() + self.my_posts.filter(is_published=True).count()


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
    
    # New fields for better organization
    author = models.CharField(max_length=200, blank=True, verbose_name="Tác giả")
    language = models.CharField(max_length=10, default='vi', verbose_name="Ngôn ngữ")
    tags = models.CharField(max_length=500, blank=True, verbose_name="Tags (phân cách bằng dấu phẩy)")

    class Meta:
        verbose_name = "Nguồn Blog"
        verbose_name_plural = "Nguồn Blog"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def posts_count(self):
        return self.posts.count()

    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


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
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name="Danh mục"
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


class MyPost(models.Model):
    title = models.CharField(max_length=500, verbose_name="Tiêu đề")
    slug = models.SlugField(max_length=500, unique=True, verbose_name="Slug")
    content = models.TextField(verbose_name="Nội dung")
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="Mô tả ngắn")
    thumbnail_url = models.URLField(blank=True, verbose_name="Ảnh thumbnail")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='my_posts',
        verbose_name="Danh mục"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Tác giả"
    )
    is_published = models.BooleanField(default=False, verbose_name="Đã xuất bản")
    is_featured = models.BooleanField(default=False, verbose_name="Nổi bật")
    published_date = models.DateTimeField(null=True, blank=True, verbose_name="Ngày xuất bản")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0, verbose_name="Lượt xem")
    tags = models.CharField(max_length=500, blank=True, verbose_name="Tags (phân cách bằng dấu phẩy)")

    class Meta:
        verbose_name = "Bài viết của tôi"
        verbose_name_plural = "Bài viết của tôi"
        ordering = ['-published_date', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_date:
            self.published_date = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('aggregator:my_post_detail', kwargs={'slug': self.slug})

    @property
    def short_excerpt(self):
        if self.excerpt:
            return self.excerpt
        if self.content and len(self.content) > 150:
            return self.content[:150] + "..."
        return self.content or ""

    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    @property
    def reading_time(self):
        # Estimate reading time (avg 200 words per minute)
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))
