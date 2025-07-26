#!/usr/bin/env python3
"""
Script để fix timezone warning trong command fetch_feeds
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloghub.settings')
django.setup()

from django.utils import timezone
from aggregator.models import Post

print("Fixing timezone issues...")

# Update all posts that have naive datetime
posts_updated = 0
for post in Post.objects.all():
    if post.published_date.tzinfo is None:
        # Convert naive datetime to aware datetime
        aware_datetime = timezone.make_aware(post.published_date)
        post.published_date = aware_datetime
        post.save(update_fields=['published_date'])
        posts_updated += 1

print(f"✅ Updated {posts_updated} posts with timezone info")
print("🎉 Timezone fix completed!")