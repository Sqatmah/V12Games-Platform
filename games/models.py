from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Genre(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Game(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    version = models.CharField(max_length=50)
    release_year = models.IntegerField()
    file_size = models.CharField(max_length=30)
    poster = models.ImageField(upload_to='posters/')
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    trailer_url = models.CharField(max_length=500, blank=True)
    genres = models.ManyToManyField(Genre, related_name='games')
    views = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    is_trending = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_upcoming = models.BooleanField(default=False)

    # متطلبات التشغيل
    min_os = models.CharField(max_length=100, blank=True, default='Windows 10 64-bit')
    min_cpu = models.CharField(max_length=200, blank=True, default='Intel Core i5')
    min_ram = models.CharField(max_length=50, blank=True, default='8 GB RAM')
    min_gpu = models.CharField(max_length=200, blank=True, default='NVIDIA GTX 970')
    min_storage = models.CharField(max_length=50, blank=True, default='50 GB')
    rec_os = models.CharField(max_length=100, blank=True, default='Windows 11 64-bit')
    rec_cpu = models.CharField(max_length=200, blank=True, default='Intel Core i7')
    rec_ram = models.CharField(max_length=50, blank=True, default='16 GB RAM')
    rec_gpu = models.CharField(max_length=200, blank=True, default='NVIDIA RTX 2070')
    rec_storage = models.CharField(max_length=50, blank=True)

    # دليل التثبيت
    install_guide = models.TextField(blank=True, default='1. Extract the downloaded archive\n2. Run the game executable\n3. Enjoy!')
    important_notes = models.TextField(blank=True, default='• Disable antivirus before extracting\n• Run as administrator\n• Install Visual C++ Redistributable if needed')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Game.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('game_detail', kwargs={'slug': self.slug})

    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return 0
        total = sum(r.rating for r in reviews)
        return round(total / reviews.count(), 1)

    def average_rating_stars(self):
        avg = self.average_rating()
        full = int(avg)
        return '★' * full + '☆' * (5 - full)

    def __str__(self):
        return self.title


class DownloadLink(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='download_links'
    )
    label = models.CharField(max_length=100)
    url = models.URLField(max_length=2000)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['label']

    def __str__(self):
        return f'{self.game.title} - {self.label}'


class Screenshot(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='screenshots'
    )
    image = models.ImageField(upload_to='screenshots/')
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f'{self.game.title} screenshot'


class Collection(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to='collections/', blank=True, null=True)
    games = models.ManyToManyField(Game, related_name='collections')

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Collection.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class GameRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('added', 'Added'),
        ('rejected', 'Rejected'),
    ]
    game_title = models.CharField(max_length=200)
    user = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='game_requests'
    )
    user_email = models.EmailField(blank=True)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    votes = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-votes', '-created_at']

    def __str__(self):
        return f'{self.game_title} ({self.status})'
