from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'مزامنة شاملة — ألعاب + مجموعات + أخبار'

    def handle(self, *args, **options):
        self.stdout.write('=' * 50)
        self.stdout.write('🚀 بدء المزامنة الشاملة')
        self.stdout.write('=' * 50)

        # 1. ألعاب جديدة
        self.stdout.write('\n📥 الخطوة 1: استيراد ألعاب جديدة...')
        call_command('sync_new_games', count=15, days=7)

        # 2. مجموعات تلقائية
        self.stdout.write('\n📦 الخطوة 2: تحديث المجموعات...')
        call_command('auto_collections')

        # 3. أخبار الألعاب
        self.stdout.write('\n📰 الخطوة 3: جلب أخبار الألعاب...')
        call_command('sync_gaming_news', count=5)

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('🎉 اكتملت المزامنة الشاملة!'))
        self.stdout.write('=' * 50)
