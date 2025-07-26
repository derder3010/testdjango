import feedparser
import logging
from datetime import datetime
from dateutil import parser as date_parser
from django.core.management.base import BaseCommand
from django.utils import timezone
from aggregator.models import BlogSource, Post

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch RSS feeds from all active blog sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-id',
            type=int,
            help='Crawl specific blog source by ID',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Limit number of posts to fetch per source (default: 50)',
        )

    def handle(self, *args, **options):
        source_id = options.get('source_id')
        limit = options.get('limit')

        if source_id:
            try:
                sources = [BlogSource.objects.get(id=source_id, is_active=True)]
                self.stdout.write(f"Crawling specific source: {sources[0].name}")
            except BlogSource.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Blog source with ID {source_id} not found or inactive')
                )
                return
        else:
            sources = BlogSource.objects.filter(is_active=True)
            self.stdout.write(f"Crawling {sources.count()} active blog sources...")

        total_new_posts = 0
        
        for source in sources:
            self.stdout.write(f"\nProcessing: {source.name}")
            self.stdout.write(f"RSS URL: {source.rss_url}")
            
            try:
                new_posts = self.fetch_source_feed(source, limit)
                total_new_posts += new_posts
                
                # Update last fetched time
                source.last_fetched = timezone.now()
                source.save(update_fields=['last_fetched'])
                
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Added {new_posts} new posts from {source.name}")
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Error processing {source.name}: {str(e)}")
                )
                logger.error(f"Error fetching {source.name}: {str(e)}")

        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 Crawling completed! Total new posts: {total_new_posts}")
        )

    def fetch_source_feed(self, source, limit):
        """Fetch and parse RSS feed for a specific source"""
        try:
            # Parse RSS feed
            feed = feedparser.parse(source.rss_url)
            
            if hasattr(feed, 'bozo') and feed.bozo:
                self.stdout.write(
                    self.style.WARNING(f"⚠ RSS feed may have issues: {source.rss_url}")
                )

            new_posts_count = 0
            processed = 0
            
            for entry in feed.entries[:limit]:
                processed += 1
                
                # Skip if post already exists
                link = getattr(entry, 'link', '')
                if not link or Post.objects.filter(link=link).exists():
                    continue

                # Extract post data
                title = getattr(entry, 'title', 'No Title')
                
                # Get excerpt from summary or description
                excerpt = ''
                if hasattr(entry, 'summary'):
                    excerpt = self.clean_html(entry.summary)
                elif hasattr(entry, 'description'):
                    excerpt = self.clean_html(entry.description)

                # Parse published date
                published_date = self.parse_published_date(entry)

                # Extract thumbnail
                thumbnail_url = self.extract_thumbnail(entry)

                # Create new post
                try:
                    Post.objects.create(
                        title=title[:500],  # Limit title length
                        link=link,
                        excerpt=excerpt,
                        thumbnail_url=thumbnail_url,
                        published_date=published_date,
                        blog_source=source
                    )
                    new_posts_count += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠ Could not save post '{title}': {str(e)}")
                    )

            self.stdout.write(f"  Processed {processed} entries, {new_posts_count} new posts")
            return new_posts_count
            
        except Exception as e:
            raise Exception(f"Failed to fetch RSS: {str(e)}")

    def parse_published_date(self, entry):
        """Parse published date from RSS entry"""
        # Try different date fields
        date_fields = ['published', 'updated', 'created']
        
        for field in date_fields:
            if hasattr(entry, field):
                try:
                    date_str = getattr(entry, field)
                    parsed_date = date_parser.parse(date_str)
                    
                    # Convert to timezone-aware datetime if needed
                    if parsed_date.tzinfo is None:
                        parsed_date = timezone.make_aware(parsed_date)
                    
                    return parsed_date
                except:
                    continue
        
        # If no date found, use current time
        return timezone.now()

    def extract_thumbnail(self, entry):
        """Extract thumbnail image from RSS entry"""
        thumbnail_url = ''
        
        # Try to get from media_thumbnail
        if hasattr(entry, 'media_thumbnail'):
            if entry.media_thumbnail and len(entry.media_thumbnail) > 0:
                thumbnail_url = entry.media_thumbnail[0].get('url', '')
        
        # Try to get from enclosures
        if not thumbnail_url and hasattr(entry, 'enclosures'):
            for enclosure in entry.enclosures:
                if enclosure.get('type', '').startswith('image/'):
                    thumbnail_url = enclosure.get('href', '')
                    break
        
        # Try to get from links
        if not thumbnail_url and hasattr(entry, 'links'):
            for link in entry.links:
                if link.get('type', '').startswith('image/'):
                    thumbnail_url = link.get('href', '')
                    break
        
        return thumbnail_url

    def clean_html(self, text):
        """Remove HTML tags from text"""
        import re
        if not text:
            return ''
        
        # Remove HTML tags
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', text)
        
        # Clean up whitespace
        text = ' '.join(text.split())
        
        # Limit length
        if len(text) > 500:
            text = text[:500] + '...'
            
        return text