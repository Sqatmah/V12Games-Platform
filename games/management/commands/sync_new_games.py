import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
from games.models import Game, Genre, Screenshot

RAWG_KEY = settings.RAWG_API_KEY
BASE = 'https://api.rawg.io/api'


class Command(BaseCommand):
    help = 'مزامنة أحدث الألعاب تلقائياً من RAWG'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='عدد الألعاب')
        parser.add_argument('--days', type=int, default=30, help='الألعاب الصادرة خلال كم يوم')

    def handle(self, *args, **options):
        count = options['count']
        days = options['days']

        # تاريخ اليوم والشهر الماضي
        today = timezone.now().date()
        from datetime import timedelta
        past = today - timedelta(days=days)

        self.stdout.write(f'🔍 جلب أحدث {count} لعبة...')

        # جلب الألعاب الحديثة مرتبة بالإصدار
        res = requests.get(f'{BASE}/games', params={
            'key': RAWG_KEY,
            'dates': f'{past},{today}',
            'ordering': '-released',
            'page_size': count,
            'platforms': '4',  # PC فقط
        }, timeout=15)

        if res.status_code != 200:
            self.stdout.write(self.style.ERROR(f'❌ خطأ في API: {res.status_code}'))
            return

        data = res.json()
        imported = 0
        updated = 0

        for item in data.get('results', []):
            slug = item.get('slug', '')
            if not slug:
                continue

            # جلب تفاصيل كاملة
            detail_res = requests.get(
                f'{BASE}/games/{slug}',
                params={'key': RAWG_KEY},
                timeout=10
            )
            if detail_res.status_code != 200:
                continue

            detail = detail_res.json()

            # هل اللعبة موجودة؟
            existing = Game.objects.filter(slug=slug).first()

            if existing:
                # تحديث فقط إذا كانت بيانات ناقصة
                changed = False
                if not existing.cover and detail.get('background_image_additional'):
                    self._download_image(existing, 'cover', detail['background_image_additional'], f'{slug}_cover.jpg')
                    changed = True
                if not existing.trailer_url:
                    trailer = self._get_trailer(slug)
                    if trailer:
                        existing.trailer_url = trailer
                        changed = True
                if changed:
                    existing.save()
                    updated += 1
                    self.stdout.write(f'🔄 تحديث: {item["name"]}')
                else:
                    self.stdout.write(f'⏭️  موجود: {item["name"]}')
                continue

            # إنشاء لعبة جديدة
            released = item.get('released', '')
            year = int(released[:4]) if released and len(released) >= 4 else 2024

            game = Game(
                title=item['name'],
                slug=slug,
                description=detail.get('description_raw', '')[:2000] or f'{item["name"]} — Available on PC.',
                version='Latest',
                release_year=year,
                file_size='Check download',
                is_trending=item.get('added', 0) > 3000,
                is_featured=item.get('metacritic', 0) >= 80 if item.get('metacritic') else False,
            )
            game.save()

            # تحميل البوستر
            poster_url = item.get('background_image')
            if poster_url:
                self._download_image(game, 'poster', poster_url, f'{slug}_poster.jpg')

            # تحميل الكفر
            cover_url = detail.get('background_image_additional')
            if cover_url:
                self._download_image(game, 'cover', cover_url, f'{slug}_cover.jpg')

            # الفيديو التشويقي
            trailer = self._get_trailer(slug)
            if trailer:
                game.trailer_url = trailer
                game.save(update_fields=['trailer_url'])

            # الأنواع
            for genre_data in item.get('genres', []):
                genre, _ = Genre.objects.get_or_create(
                    slug=genre_data['slug'],
                    defaults={'name': genre_data['name']}
                )
                game.genres.add(genre)

            # الـ Screenshots
            self._get_screenshots(game, slug)

            # متطلبات التشغيل
            self._set_requirements(game, detail)

            imported += 1
            self.stdout.write(self.style.SUCCESS(f'✅ {item["name"]} ({year})'))

        # إضافة روابط التحميل للألعاب الجديدة
        self._add_download_links()

        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 مكتمل! استيراد: {imported} | تحديث: {updated}'
        ))

    def _download_image(self, game, field, url, filename):
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                getattr(game, field).save(filename, ContentFile(res.content), save=True)
        except Exception:
            pass

    def _get_trailer(self, slug):
        try:
            res = requests.get(
                f'{BASE}/games/{slug}/movies',
                params={'key': RAWG_KEY},
                timeout=8
            )
            if res.status_code == 200:
                movies = res.json().get('results', [])
                if movies:
                    data = movies[0].get('data', {})
                    return data.get('max') or data.get('480') or ''
        except Exception:
            pass
        return ''

    def _get_screenshots(self, game, slug):
        try:
            res = requests.get(
                f'{BASE}/games/{slug}/screenshots',
                params={'key': RAWG_KEY},
                timeout=8
            )
            if res.status_code == 200:
                shots = res.json().get('results', [])[:4]
                for i, ss in enumerate(shots):
                    url = ss.get('image')
                    if url:
                        try:
                            img = requests.get(url, timeout=8)
                            if img.status_code == 200:
                                s = Screenshot(game=game)
                                s.image.save(f'{slug}_ss{i}.jpg', ContentFile(img.content), save=True)
                        except Exception:
                            pass
        except Exception:
            pass

    def _set_requirements(self, game, detail):
        try:
            reqs = detail.get('requirements_en', {}) or {}
            min_req = reqs.get('minimum', '')
            rec_req = reqs.get('recommended', '')

            def extract(text, key):
                import re
                pattern = rf'{key}:?\s*([^\n<]+)'
                m = re.search(pattern, text, re.IGNORECASE)
                return m.group(1).strip()[:150] if m else ''

            if min_req:
                game.min_os  = extract(min_req, 'OS') or game.min_os
                game.min_cpu = extract(min_req, 'Processor') or game.min_cpu
                game.min_ram = extract(min_req, 'Memory') or game.min_ram
                game.min_gpu = extract(min_req, 'Graphics') or game.min_gpu

            if rec_req:
                game.rec_os  = extract(rec_req, 'OS') or game.rec_os
                game.rec_cpu = extract(rec_req, 'Processor') or game.rec_cpu
                game.rec_ram = extract(rec_req, 'Memory') or game.rec_ram
                game.rec_gpu = extract(rec_req, 'Graphics') or game.rec_gpu

            game.save()
        except Exception:
            pass

    def _add_download_links(self):
        from urllib.parse import quote
        from games.models import DownloadLink
        games_no_links = Game.objects.filter(download_links__isnull=True)
        for game in games_no_links:
            encoded = quote(game.title)
            links = [
                ('🎮 AnkerGames — Safe & Direct', f'https://ankergames.net/?s={encoded}'),
                ('🔍 FitGirl Repacks', f'https://fitgirl-repacks.site/?s={encoded}'),
                ('🔍 DODI Repacks', f'https://dodi-repacks.site/?s={encoded}'),
            ]
            for label, url in links:
                DownloadLink.objects.create(game=game, label=label, url=url, is_active=True)