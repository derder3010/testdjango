# BlogHub - Tổng hợp Blog Cá nhân

Một ứng dụng Django đơn giản để tổng hợp và hiển thị metadata bài viết từ các blog cá nhân thông qua RSS feed.

## 🚀 Tính năng

- ✅ Tổng hợp bài viết từ RSS feed của các blog cá nhân
- ✅ Hiển thị metadata: tiêu đề, link, mô tả ngắn, ảnh thumbnail
- ✅ Không lưu nội dung chi tiết, chỉ link đến bài gốc
- ✅ Filter theo blog nguồn và tìm kiếm
- ✅ Giao diện responsive với Tailwind CSS
- ✅ HTMX cho pagination và filter động
- ✅ Django Admin để quản lý blog nguồn
- ✅ REST API (tùy chọn)

## 🛠️ Công nghệ sử dụng

- **Backend**: Django 4.2 + Django REST Framework
- **Frontend**: HTML + Tailwind CSS + HTMX
- **Database**: SQLite (mặc định)
- **RSS Parser**: feedparser
- **CSS Framework**: Tailwind CSS
- **JavaScript**: HTMX

## ⚡ Setup nhanh

### 1. Clone và cài đặt

```bash
# Clone project (hoặc tạo project mới từ code này)
cd bloghub

# Tạo virtual environment (khuyến nghị)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt
```

### 2. Khởi tạo database

```bash
# Tạo migration
python manage.py makemigrations

# Chạy migration
python manage.py migrate

# Tạo superuser để truy cập admin
python manage.py createsuperuser
```

### 3. Chạy server

```bash
python manage.py runserver
```

Truy cập:
- **Trang chính**: http://127.0.0.1:8000/
- **Django Admin**: http://127.0.0.1:8000/admin/
- **Blog nguồn**: http://127.0.0.1:8000/blog-sources/
- **API**: http://127.0.0.1:8000/api/

## 📝 Hướng dẫn sử dụng

### 1. Thêm blog nguồn

1. Truy cập Django Admin: `/admin/`
2. Đăng nhập với superuser đã tạo
3. Vào **Aggregator > Blog Sources**
4. Thêm blog mới với:
   - Tên blog
   - Mô tả (tùy chọn)
   - RSS URL (bắt buộc)
   - Trang chủ (tùy chọn)
   - Logo URL (tùy chọn)

### 2. Crawl bài viết

```bash
# Crawl tất cả blog nguồn đang hoạt động
python manage.py fetch_feeds

# Crawl blog cụ thể theo ID
python manage.py fetch_feeds --source-id 1

# Giới hạn số bài viết crawl mỗi nguồn
python manage.py fetch_feeds --limit 10
```

### 3. Tự động crawl định kỳ

Bạn có thể thiết lập cron job để crawl tự động:

```bash
# Thêm vào crontab để crawl mỗi 30 phút
*/30 * * * * cd /path/to/bloghub && python manage.py fetch_feeds >> crawl.log 2>&1
```

## 🎨 Giao diện

### Trang chính
- Hero section với giới thiệu
- Filter theo blog nguồn và tìm kiếm
- Grid hiển thị bài viết với:
  - Ảnh thumbnail
  - Tiêu đề (link đến bài gốc)
  - Mô tả ngắn
  - Tên blog nguồn
  - Ngày đăng
- Pagination với HTMX

### Trang blog nguồn
- Thống kê tổng quan
- Danh sách blog với logo, mô tả
- Số lượng bài viết từng blog
- Link đến trang chủ blog

## 🔧 Cấu hình

### Settings Django quan trọng

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'aggregator',
]

# Cấu hình REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# Timezone
TIME_ZONE = 'Asia/Ho_Chi_Minh'
LANGUAGE_CODE = 'vi'
```

## 📊 REST API Endpoints

- `GET /api/blog-sources/` - Danh sách blog nguồn
- `GET /api/posts/` - Danh sách bài viết
- `GET /api/posts/?blog_source=1` - Lọc theo blog
- `GET /api/stats/` - Thống kê tổng quan

## 🚀 Production Deploy

### 1. Cập nhật settings

```python
# settings/production.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# Static files
STATIC_ROOT = '/var/www/bloghub/static/'

# Database (PostgreSQL khuyến nghị)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bloghub',
        'USER': 'bloghub_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 2. Collect static files

```bash
python manage.py collectstatic
```

### 3. Setup web server (Nginx + Gunicorn)

```bash
# Cài đặt Gunicorn
pip install gunicorn

# Chạy với Gunicorn
gunicorn bloghub.wsgi:application --bind 0.0.0.0:8000
```

## 🔍 Troubleshooting

### Lỗi thường gặp

1. **RSS không parse được**
   - Kiểm tra URL RSS có hợp lệ
   - Kiểm tra blog có còn hoạt động không

2. **Không có ảnh thumbnail**
   - Một số RSS không có ảnh
   - Kiểm tra URL ảnh có hợp lệ không

3. **Encoding issues**
   - Đảm bảo database hỗ trợ UTF-8
   - Kiểm tra encoding của RSS feed

## 📈 Tối ưu hiệu suất

1. **Database**
   - Thêm index cho trường `published_date`
   - Sử dụng `select_related()` cho foreign key

2. **Caching**
   - Cache RSS feed trong thời gian ngắn
   - Cache danh sách blog nguồn

3. **CDN**
   - Sử dụng CDN cho static files
   - Tối ưu ảnh thumbnail

## 🤝 Đóng góp

1. Fork project
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - xem file LICENSE để biết thêm chi tiết.

## 📞 Hỗ trợ

Nếu gặp vấn đề, hãy tạo issue trên GitHub hoặc liên hệ qua email.

---

**Tạo bởi**: BlogHub Team  
**Ngày**: 2024  
**Version**: 1.0.0