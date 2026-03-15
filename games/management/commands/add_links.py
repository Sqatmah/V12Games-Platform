from django.core.management.base import BaseCommand
from games.models import Game, DownloadLink
from urllib.parse import quote


class Command(BaseCommand):
    help = 'إضافة روابط تحميل آمنة لكل الألعاب'

    def handle(self, *args, **options):
        games = Game.objects.all()
        added = 0

        for game in games:
            # تجاهل اللعبة إذا عندها روابط مسبقاً
            if game.download_links.exists():
                self.stdout.write(f'⏭️  موجود: {game.title}')
                continue

            # اسم اللعبة مشفر للرابط
            encoded = quote(game.title)

            # روابط آمنة وموثوقة فقط
            links = [
                {
                    'label': '🎮 AnkerGames — آمن ومباشر',
                    'url': f'https://ankergames.net/?s={encoded}',
                },
                {
                    'label': '🔍 FitGirl Repacks',
                    'url': f'https://fitgirl-repacks.site/?s={encoded}',
                },
                {
                    'label': '🔍 DODI Repacks',
                    'url': f'https://dodi-repacks.site/?s={encoded}',
                },
            ]

            for link_data in links:
                DownloadLink.objects.create(
                    game=game,
                    label=link_data['label'],
                    url=link_data['url'],
                    is_active=True,
                )

            added += 1
            self.stdout.write(
                self.style.SUCCESS(f'✅ أضيفت روابط: {game.title}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 تم إضافة روابط لـ {added} لعبة!')
        )