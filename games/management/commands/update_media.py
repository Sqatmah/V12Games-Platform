import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from games.models import Game, Screenshot

RAWG_KEY = settings.RAWG_API_KEY
BASE_URL = 'https://api.rawg.io/api'


class Command(BaseCommand):
    help = 'تحديث صور وفيديوهات الألعاب من RAWG'

    def handle(self, *args, **options):
        games = Game.objects.all()
        updated = 0

        for game in games:
            self.stdout.write(f'🔍 جاري تحديث: {game.title}')

            # ── جلب تفاصيل اللعبة ──
            res = requests.get(
                f'{BASE_URL}/games/{game.slug}',
                params={'key': RAWG_KEY},
                timeout=10
            )
            if res.status_code != 200:
                self.stdout.write(f'  ⚠️  لم يُعثر على: {game.title}')
                continue

            data = res.json()
            changed = False

            # ── تحديث البوستر ──
            poster_url = data.get('background_image')
            if poster_url and not game.poster:
                try:
                    img = requests.get(poster_url, timeout=10)
                    if img.status_code == 200:
                        game.poster.save(
                            f'{game.slug}_poster.jpg',
                            ContentFile(img.content),
                            save=False
                        )
                        changed = True
                        self.stdout.write(f'  🖼️  بوستر محدّث')
                except Exception as e:
                    self.stdout.write(f'  ⚠️  خطأ بوستر: {e}')

            # ── تحديث صورة الكفر ──
            cover_url = data.get('background_image_additional')
            if cover_url and not game.cover:
                try:
                    img = requests.get(cover_url, timeout=10)
                    if img.status_code == 200:
                        game.cover.save(
                            f'{game.slug}_cover.jpg',
                            ContentFile(img.content),
                            save=False
                        )
                        changed = True
                        self.stdout.write(f'  🎨 كفر محدّث')
                except Exception as e:
                    self.stdout.write(f'  ⚠️  خطأ كفر: {e}')

            # ── تحديث الوصف ──
            description = data.get('description_raw', '')
            if description and game.description in ['No description available.', '']:
                game.description = description[:2000]
                changed = True
                self.stdout.write(f'  📝 وصف محدّث')

            if changed:
                game.save()

            # ── جلب الفيديو التشويقي ──
            if not game.trailer_url:
                movies_res = requests.get(
                    f'{BASE_URL}/games/{game.slug}/movies',
                    params={'key': RAWG_KEY},
                    timeout=10
                )
                if movies_res.status_code == 200:
                    movies = movies_res.json().get('results', [])
                    if movies:
                        video_url = movies[0].get('data', {}).get('max') or \
                                    movies[0].get('data', {}).get('480')
                        if video_url:
                            game.trailer_url = video_url
                            game.save(update_fields=['trailer_url'])
                            changed = True
                            self.stdout.write(f'  🎬 فيديو محدّث')

            # ── جلب Screenshots ──
            if not game.screenshots.exists():
                ss_res = requests.get(
                    f'{BASE_URL}/games/{game.slug}/screenshots',
                    params={'key': RAWG_KEY},
                    timeout=10
                )
                if ss_res.status_code == 200:
                    screenshots = ss_res.json().get('results', [])
                    count = 0
                    for ss in screenshots[:4]:
                        img_url = ss.get('image')
                        if not img_url:
                            continue
                        try:
                            img = requests.get(img_url, timeout=10)
                            if img.status_code == 200:
                                s = Screenshot(game=game)
                                s.image.save(
                                    f'{game.slug}_ss_{count}.jpg',
                                    ContentFile(img.content),
                                    save=True
                                )
                                count += 1
                        except Exception:
                            pass
                    if count > 0:
                        self.stdout.write(f'  📸 {count} صور إضافية')

            updated += 1
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم: {game.title}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 تم تحديث {updated} لعبة بنجاح!')
        )
