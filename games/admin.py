from django.contrib import admin
from .models import Game, Genre, Collection, DownloadLink, Screenshot, GameRequest


class DownloadLinkInline(admin.TabularInline):
    model = DownloadLink
    extra = 2
    fields = ['label', 'url', 'is_active']


class ScreenshotInline(admin.TabularInline):
    model = Screenshot
    extra = 3


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['title', 'version', 'release_year', 'downloads', 'views', 'is_trending', 'is_featured']
    list_filter = ['genres', 'is_trending', 'is_featured', 'is_upcoming']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_trending', 'is_featured']
    inlines = [DownloadLinkInline, ScreenshotInline]
    readonly_fields = ['views', 'downloads', 'likes', 'created_at', 'updated_at']
    filter_horizontal = ['genres']
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'description', 'version', 'release_year', 'file_size')
        }),
        ('Media', {
            'fields': ('poster', 'cover', 'trailer_url')
        }),
        ('Taxonomy', {
            'fields': ('genres',)
        }),
        ('Stats', {
            'fields': ('views', 'downloads', 'likes'),
            'classes': ('collapse',)
        }),
        ('Flags', {
            'fields': ('is_trending', 'is_featured', 'is_upcoming')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('System Requirements', {
    'fields': (
        'min_os', 'min_cpu', 'min_ram', 'min_gpu', 'min_storage',
        'rec_os', 'rec_cpu', 'rec_ram', 'rec_gpu', 'rec_storage',
    ),
    'classes': ('collapse',)
        }),
        ('Installation Guide', {
        'fields': ('install_guide', 'important_notes'),
        'classes': ('collapse',)
}),
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['games']


@admin.register(DownloadLink)
class DownloadLinkAdmin(admin.ModelAdmin):
    list_display = ['game', 'label', 'is_active']




@admin.register(GameRequest)
class GameRequestAdmin(admin.ModelAdmin):
    list_display = ['game_title', 'user', 'status', 'votes', 'created_at']
    list_filter = ['status']
    list_editable = ['status']
    search_fields = ['game_title']