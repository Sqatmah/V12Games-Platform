from django.core.management.base import BaseCommand
from django.core.management import call_command
import time


class Command(BaseCommand):
    help = 'تشغيل المزامنة كل 24 ساعة'

    def add_arguments(self, parser):
        parser.add_argument('--interval', type=int, default=24, help='الفاصل الزمني بالساعات')
        parser.add_argument('--count', type=int, default=10, help='عدد الألعاب في كل مزامنة')

    def handle(self, *args, **options):
        interval = options['interval']
        count = options['count']
        seconds = interval * 3600

        self.stdout.write(f'🕐 بدء الجدولة — كل {interval} ساعة')

        while True:
            self.stdout.write(f'\n🔄 تشغيل المزامنة...')
            try:
                call_command('sync_new_games', count=count)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ خطأ: {e}'))

            self.stdout.write(f'⏳ الانتظار {interval} ساعة...')
            time.sleep(seconds)