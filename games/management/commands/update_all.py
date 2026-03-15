from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'تحديث كل شيء دفعة واحدة'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='عدد الألعاب الجديدة'
        )
        parser.add_argument(
            '--query',
            type=str,
            default='',
            help='كلمة بحث محددة'
        )

    def handle(self, *args, **options):
        count = options['count']
        query = options['query']

        self.stdout.write('=' * 40)
        self.stdout.write('🚀 بدء التحديث الشامل...')
        self.stdout.write('=' * 40)

        # الخطوة 1
        self.stdout.write('\n📥 الخطوة 1: استيراد الألعاب...')
        if query:
            call_command('import_games', count=count, query=query)
        else:
            call_command('import_games', count=count)

        # الخطوة 2
        self.stdout.write('\n🔗 الخطوة 2: إضافة روابط التحميل...')
        call_command('add_links')

        # الخطوة 3
        self.stdout.write('\n🎨 الخطوة 3: تحديث الصور والفيديو...')
        call_command('update_media')

        self.stdout.write('\n' + '=' * 40)
        self.stdout.write(
            self.style.SUCCESS('🎉 اكتمل التحديث الشامل بنجاح!')
        )
        self.stdout.write('=' * 40)



#اذا بدي اضيف لعبة محددة مع التحديث 

#python manage.py update_all --query "FIFA" --count 10

#كل ما أضيف لعبة لازم اشغل هذا الأمر 

#python manage.py update_all --count 20