import feedparser
import requests
import re
import html
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from blog.models import Post
from accounts.models import User


class Command(BaseCommand):
    help = 'جلب أخبار الألعاب العربية تلقائياً'

    ARABIC_FEEDS = [
        {
            'name': 'عالم الألعاب',
            'url': 'https://3alm-alab3ab.com/feed/',
        },
        {
            'name': 'كووورة',
            'url': 'https://www.kooora.com/rss.aspx',
        },
        {
            'name': 'Gamers-Hub عربي',
            'url': 'https://gamershub.in/feed/',
        },
        {
            'name': 'IGN Arabia',
            'url': 'https://arabia.ign.com/feed.xml',
        },
        {
            'name': 'ArabHardware',
            'url': 'https://www.arabhardware.net/news/feed/',
        },
        {
            'name': 'Tech Arabia',
            'url': 'https://tech-arabia.com/feed/',
        },
    ]

    # مواضيع ترندينج نترجمها
    HOT_GAMING_TOPICS = {
        'GTA 6': 'جي تي إيه 6 — كل ما تريد معرفته عن اللعبة الأكثر انتظاراً',
        'Call of Duty': 'كول أوف ديوتي — آخر الأخبار والتحديثات',
        'Resident Evil': 'ريزيدنت إيفل — سلسلة الرعب الأشهر في التاريخ',
        'PlayStation': 'بلايستيشن — آخر أخبار الألعاب الحصرية',
        'Xbox': 'إكس بوكس — ألعاب جديدة على Game Pass',
    }

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10)

    def handle(self, *args, **options):
        count = options['count']
        self.admin = User.objects.filter(is_superuser=True).first()
        self.imported = 0
        self.count = count

        self.stdout.write('📰 جلب أخبار الألعاب العربية...\n')

        # أولاً: RSS عربي
        self._fetch_arabic_rss()

        # ثانياً: مقالات مترجمة للمواضيع الساخنة
        if self.imported < count:
            self._create_trending_articles()

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 تم نشر {self.imported} خبر عربي!')
        )

    def _fetch_arabic_rss(self):
        self.stdout.write('📡 RSS عربي...')
        for feed_info in self.ARABIC_FEEDS:
            if self.imported >= self.count:
                break
            self.stdout.write(f'  🔍 {feed_info["name"]}...')
            try:
                feed = feedparser.parse(feed_info['url'])
                for entry in feed.entries[:3]:
                    if self.imported >= self.count:
                        break
                    title = self._clean_text(entry.get('title', ''))
                    if not title:
                        continue
                    content = (
                        entry.get('content', [{}])[0].get('value', '')
                        or entry.get('summary', '')
                    )
                    body = f"""{self._clean_html(content)}

---
📰 المصدر: {feed_info['name']}
🔗 اقرأ المقال كاملاً: {entry.get('link', '')}
"""
                    self._save_post(
                        title=title,
                        body=body,
                        img_url=self._get_image(entry),
                    )
            except Exception as e:
                self.stdout.write(f'    ⚠️  {e}')

    def _create_trending_articles(self):
        self.stdout.write('\n✍️  إنشاء مقالات المواضيع الساخنة...')

        articles = [
            {
                'title': '🎮 أفضل 10 ألعاب PC مجانية يجب تحميلها في 2025',
                'body': '''في عالم الألعاب المتطور، أصبح بإمكانك الاستمتاع بتجارب رائعة بدون أي تكلفة. إليك أفضل الألعاب المجانية لعام 2025:

**1. Fortnite**
لا يزال Fortnite يحتل مكانة بارزة بين ألعاب Battle Royale المجانية، مع تحديثات مستمرة وموسم جديد مليء بالمفاجآت.

**2. Warzone**
نسخة Call of Duty المجانية تقدم تجربة قتالية لا مثيل لها بمناطق ضخمة وأسلحة متنوعة.

**3. Apex Legends**
لعبة Battle Royale الممتازة من Respawn Entertainment مع نظام حركة فريد وأبطال بقدرات خاصة.

**4. League of Legends**
أشهر ألعاب MOBA في العالم مع ملايين اللاعبين يومياً.

**5. Genshin Impact**
لعبة RPG مفتوحة العالم بجرافيك استثنائي وقصة ملحمية.

جميع هذه الألعاب متاحة للتحميل مجاناً على V12Games!''',
            },
            {
                'title': '🔥 GTA 6 — كل ما نعرفه حتى الآن عن اللعبة الأكثر انتظاراً',
                'body': '''GTA 6 هي اللعبة الأكثر ترقباً في تاريخ الألعاب. إليك كل المعلومات المؤكدة:

**الإصدار المتوقع**
تخطط Rockstar Games لإصدار GTA 6 في عام 2025، وهو ما أكدته الشركة رسمياً.

**الإعلان التشويقي**
حصد الإعلان التشويقي الأول أكثر من 100 مليون مشاهدة خلال 24 ساعة فقط، مما يجعله الأكثر مشاهدة في تاريخ ألعاب الفيديو.

**المنصات**
ستُطلق اللعبة أولاً على PlayStation 5 و Xbox Series X، ثم على PC لاحقاً.

**الشخصيات**
للمرة الأولى في سلسلة GTA الرئيسية، ستضم اللعبة بطلة امرأة تدعى Lucia.

**البيئة**
ستعود اللعبة إلى مدينة Vice City بشكل أكبر وأكثر تفصيلاً من أي وقت مضى.

ترقبوا المزيد من الأخبار على V12Games!''',
            },
            {
                'title': '💻 متطلبات تشغيل أشهر الألعاب على PC في 2025',
                'body': '''هل جهازك يدعم أحدث الألعاب؟ إليك متطلبات أشهر الألعاب:

**GTA V**
- المعالج: Intel Core i5 3470
- الذاكرة: 8 GB RAM
- كرت الشاشة: GTX 660 2GB
- المساحة: 95 GB

**Cyberpunk 2077**
- المعالج: Intel Core i7 6700
- الذاكرة: 12 GB RAM
- كرت الشاشة: RTX 2060
- المساحة: 70 GB

**Red Dead Redemption 2**
- المعالج: Intel Core i7 4770
- الذاكرة: 12 GB RAM
- كرت الشاشة: GTX 1060 6GB
- المساحة: 150 GB

**Elden Ring**
- المعالج: Intel Core i7 8700
- الذاكرة: 16 GB RAM
- كرت الشاشة: GTX 1070 8GB
- المساحة: 60 GB

جميع هذه الألعاب متاحة للتحميل على V12Games مع متطلبات التشغيل الكاملة لكل لعبة!''',
            },
            {
                'title': '⭐ أفضل ألعاب الرعب لعام 2025 — تجارب لا تُنسى',
                'body': '''عشاق الرعب، هذا المقال لكم! إليك أفضل ألعاب الرعب في 2025:

**Resident Evil Series**
السلسلة الأشهر في عالم ألعاب الرعب. من RE2 Remake إلى Village، كل جزء يقدم تجربة فريدة ومرعبة.

**Silent Hill 2 Remake**
عودة الأسطورة! إعادة تصوير كاملة للجزء الثاني من سلسلة Silent Hill بجرافيك حديث ورهيب.

**Alan Wake 2**
تحفة فنية من Remedy Entertainment تجمع بين الرعب والغموض بأسلوب سينمائي مذهل.

**Dead Space Remake**
واحدة من أفضل ألعاب الرعب في الفضاء، بصريات محسّنة وقصة أكثر عمقاً.

**Outlast Trials**
تجربة رعب تعاونية مع أصدقائك، إن كنت تجرؤ!

كل هذه الألعاب متاحة على V12Games للتحميل المجاني!''',
            },
        ]

        for article in articles:
            if self.imported >= self.count:
                break
            self._save_post(
                title=article['title'],
                body=article['body'],
            )

    def _save_post(self, title, body, img_url=None):
        slug = slugify(title)[:80]
        if not slug or Post.objects.filter(slug=slug).exists():
            return

        post = Post(
            title=title[:200],
            slug=slug,
            author=self.admin,
            body=body,
            published=True,
        )
        post.save()

        if img_url:
            try:
                img_res = requests.get(img_url, timeout=8, headers={
                    'User-Agent': 'Mozilla/5.0'
                })
                if img_res.status_code == 200:
                    post.cover_image.save(
                        f'ar_news_{post.pk}.jpg',
                        ContentFile(img_res.content),
                        save=True
                    )
            except Exception:
                pass

        self.imported += 1
        self.stdout.write(self.style.SUCCESS(f'  ✅ {title[:60]}'))

    def _clean_text(self, text):
        text = html.unescape(text)
        return re.sub(r'<[^>]+>', '', text).strip()

    def _clean_html(self, content):
        if not content:
            return ''
        content = re.sub(r'<br\s*/?>', '\n', content)
        content = re.sub(r'<p[^>]*>', '\n', content)
        content = re.sub(r'</p>', '\n', content)
        content = re.sub(r'<[^>]+>', '', content)
        content = html.unescape(content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        return content.strip()[:3000]

    def _get_image(self, entry):
        for m in entry.get('media_content', []):
            if m.get('url'):
                return m['url']
        for t in entry.get('media_thumbnail', []):
            return t.get('url', '')
        content = entry.get('content', [{}])[0].get('value', '') or entry.get('summary', '')
        m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        return m.group(1) if m else None