import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from blog.models import Post
from accounts.models import User
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'جلب أخبار الألعاب تلقائياً'

    # مصادر الأخبار — NewsAPI مجاني
    NEWS_API_KEY = getattr(settings, 'NEWS_API_KEY', '')
    NEWS_URL = 'https://newsapi.org/v2/everything'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10)

    def handle(self, *args, **options):
        count = options['count']

        if not self.NEWS_API_KEY:
            self.stdout.write(self.style.ERROR('❌ NEWS_API_KEY غير موجود في .env'))
            self.stdout.write('سجّل مجاناً في https://newsapi.org وأضف المفتاح')
            return

        # المواضيع الأكثر متابعة
        queries = [
            'GTA 6',
            'PlayStation 5 games 2025',
            'Xbox Game Pass new games',
            'PC gaming news',
            'new game release 2025',
        ]

        # جلب حساب الأدمن لنسب المقالات له
        admin = User.objects.filter(is_superuser=True).first()
        imported = 0

        for query in queries:
            if imported >= count:
                break

            res = requests.get(self.NEWS_URL, params={
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 3,
                'apiKey': self.NEWS_API_KEY,
            }, timeout=10)

            if res.status_code != 200:
                continue

            articles = res.json().get('articles', [])

            for article in articles:
                if imported >= count:
                    break

                title = article.get('title', '').strip()
                if not title or title == '[Removed]':
                    continue

                # تجاهل إذا موجود
                slug = slugify(title)[:80]
                if Post.objects.filter(slug=slug).exists():
                    self.stdout.write(f'⏭️  موجود: {title[:50]}')
                    continue

                # المحتوى
                content = article.get('content') or article.get('description') or ''
                content = content.replace('[+', '').replace('chars]', '').strip()
                source = article.get('source', {}).get('name', 'Gaming News')
                url = article.get('url', '')

                body = f"""{content}

---
📰 Source: {source}
🔗 Read full article: {url}
📅 Published: {article.get('publishedAt', '')[:10]}
"""

                # أنشئ المقال
                post = Post(
                    title=title[:200],
                    slug=slug,
                    author=admin,
                    body=body,
                    published=True,
                )
                post.save()

                # تحميل صورة الغلاف
                img_url = article.get('urlToImage')
                if img_url:
                    try:
                        img = requests.get(img_url, timeout=8)
                        if img.status_code == 200:
                            ext = img_url.split('.')[-1].split('?')[0][:4]
                            post.cover_image.save(
                                f'news_{post.pk}.{ext}',
                                ContentFile(img.content),
                                save=True
                            )
                    except Exception:
                        pass

                imported += 1
                self.stdout.write(self.style.SUCCESS(f'✅ {title[:60]}'))

        self.stdout.write(self.style.SUCCESS(f'\n🎉 تم نشر {imported} خبر جديد!'))
