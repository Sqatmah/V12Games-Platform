import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from games.models import Game, Genre

RAWG_KEY = settings.RAWG_API_KEY
BASE_URL = 'https://api.rawg.io/api'


class Command(BaseCommand):
    help = 'استيراد الألعاب من RAWG API'

    def add_arguments(self, parser):
        parser.add_argument('--query', type=str, default='', help='كلمة البحث')
        parser.add_argument('--count', type=int, default=10, help='عدد الألعاب')

    def handle(self, *args, **options):
        query = options['query']
        count = options['count']

        self.stdout.write(f'🎮 جاري استيراد {count} لعبة...')

        params = {
            'key': RAWG_KEY,
            'page_size': count,
            'ordering': '-added',
        }
        if query:
            params['search'] = query

        res = requests.get(f'{BASE_URL}/games', params=params)
        data = res.json()

        imported = 0
        for item in data.get('results', []):

            if Game.objects.filter(slug=item['slug']).exists():
                self.stdout.write(f'⏭️  موجودة: {item["name"]}')
                continue

            # جلب تفاصيل اللعبة
            detail_res = requests.get(
                f'{BASE_URL}/games/{item["slug"]}',
                params={'key': RAWG_KEY}
            )
            detail = detail_res.json()

            # إنشاء اللعبة
            game = Game(
                title=item['name'],
                slug=item['slug'],
                description=detail.get('description_raw', 'No description available.')[:2000],
                version='Latest',
                release_year=int(item.get('released', '2020-01-01')[:4]) if item.get('released') else 2020,
                file_size='Check download',
                is_trending=item.get('added', 0) > 5000,
            )
            game.save()

            # تحميل صورة البوستر
            poster_url = item.get('background_image')
            if poster_url:
                try:
                    img_res = requests.get(poster_url, timeout=10)
                    if img_res.status_code == 200:
                        game.poster.save(
                            f'{item["slug"]}.jpg',
                            ContentFile(img_res.content),
                            save=True
                        )
                except Exception as e:
                    self.stdout.write(f'⚠️  خطأ في الصورة: {e}')

            # إضافة الأنواع
            for genre_data in item.get('genres', []):
                genre, _ = Genre.objects.get_or_create(
                    slug=genre_data['slug'],
                    defaults={'name': genre_data['name']}
                )
                game.genres.add(genre)

            imported += 1
            self.stdout.write(
                self.style.SUCCESS(f'✅ تم استيراد: {item["name"]}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 تم استيراد {imported} لعبة بنجاح!')
        )
