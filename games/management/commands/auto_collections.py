from django.core.management.base import BaseCommand
from games.models import Game, Collection
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'إنشاء مجموعات تلقائية لسلاسل الألعاب'

    # قائمة السلاسل المعروفة
    SERIES = {
        'Resident Evil': {
            'keywords': ['resident evil', 'biohazard'],
            'description': 'The legendary survival horror franchise by Capcom.',
            'icon': '🧟'
        },
        'FIFA / EA Sports FC': {
            'keywords': ['fifa', 'ea sports fc'],
            'description': 'The world\'s most popular football game series.',
            'icon': '⚽'
        },
        'Grand Theft Auto': {
            'keywords': ['grand theft auto', 'gta'],
            'description': 'Rockstar\'s iconic open-world crime series.',
            'icon': '🚗'
        },
        'Call of Duty': {
            'keywords': ['call of duty', 'cod', 'warzone', 'modern warfare'],
            'description': 'Activision\'s blockbuster first-person shooter series.',
            'icon': '🔫'
        },
        'Assassin\'s Creed': {
            'keywords': ["assassin's creed", 'assassins creed'],
            'description': 'Ubisoft\'s historical action-adventure series.',
            'icon': '🗡️'
        },
        'The Witcher': {
            'keywords': ['witcher'],
            'description': 'CD Projekt Red\'s acclaimed RPG series.',
            'icon': '⚔️'
        },
        'Red Dead': {
            'keywords': ['red dead'],
            'description': 'Rockstar\'s epic western adventure series.',
            'icon': '🤠'
        },
        'Far Cry': {
            'keywords': ['far cry'],
            'description': 'Ubisoft\'s open-world first-person shooter series.',
            'icon': '🌴'
        },
        'Battlefield': {
            'keywords': ['battlefield'],
            'description': 'EA\'s large-scale military shooter series.',
            'icon': '💣'
        },
        'Need for Speed': {
            'keywords': ['need for speed', 'nfs'],
            'description': 'EA\'s iconic street racing series.',
            'icon': '🏎️'
        },
        'Batman Arkham': {
            'keywords': ['batman', 'arkham'],
            'description': 'The acclaimed Batman game series by Rocksteady.',
            'icon': '🦇'
        },
        'Dark Souls / Elden Ring': {
            'keywords': ['dark souls', 'elden ring', 'sekiro', 'bloodborne', 'demon souls'],
            'description': 'FromSoftware\'s legendary soulslike series.',
            'icon': '💀'
        },
        'The Elder Scrolls': {
            'keywords': ['elder scrolls', 'skyrim', 'oblivion', 'morrowind'],
            'description': 'Bethesda\'s massive open-world RPG series.',
            'icon': '🐉'
        },
        'Fallout': {
            'keywords': ['fallout'],
            'description': 'Bethesda\'s post-apocalyptic RPG series.',
            'icon': '☢️'
        },
        'God of War': {
            'keywords': ['god of war'],
            'description': 'Sony\'s epic mythology action series.',
            'icon': '⚡'
        },
        'BioShock': {
            'keywords': ['bioshock'],
            'description': 'The iconic dystopian first-person shooter series.',
            'icon': '🌊'
        },
        'Borderlands': {
            'keywords': ['borderlands'],
            'description': 'Gearbox\'s popular looter-shooter series.',
            'icon': '🔮'
        },
        'Tomb Raider': {
            'keywords': ['tomb raider', 'lara croft'],
            'description': 'Lara Croft\'s adventure series.',
            'icon': '🏛️'
        },
        'Half-Life / Portal': {
            'keywords': ['half-life', 'half life', 'portal'],
            'description': 'Valve\'s revolutionary FPS and puzzle series.',
            'icon': '🔬'
        },
        'Left 4 Dead': {
            'keywords': ['left 4 dead', 'left4dead'],
            'description': 'Valve\'s iconic co-op zombie shooter series.',
            'icon': '🧠'
        },
    }

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for series_name, config in self.SERIES.items():
            keywords = config['keywords']
            icon = config.get('icon', '🎮')

            # ابحث عن الألعاب المطابقة
            games = set()
            for keyword in keywords:
                matched = Game.objects.filter(title__icontains=keyword)
                for g in matched:
                    games.add(g)

            if not games:
                continue

            # أنشئ أو حدّث المجموعة
            slug = slugify(series_name)
            collection, is_new = Collection.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': f'{icon} {series_name}',
                    'description': config['description'],
                }
            )

            # أضف الألعاب
            for game in games:
                collection.games.add(game)

            if is_new:
                created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ إنشاء: {series_name} ({len(games)} ألعاب)')
                )
            else:
                updated += 1
                self.stdout.write(f'🔄 تحديث: {series_name} ({len(games)} ألعاب)')

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 إنشاء: {created} | تحديث: {updated} مجموعة')
        )