from django.contrib import admin
from .models import User, Lobby, Game, Player


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'password_display', 'is_active', 'is_online', 'created_at', 'last_seen')
    list_filter = ('is_active', 'is_online')
    date_hierarchy = 'created_at'
    list_display_links = ['username']
    search_fields = ('username', 'email')

    @admin.display()
    def password_display(self, obj):
        return '••••••••'

    password_display.short_description = 'Пароль (зашифрован)'


@admin.register(Lobby)
class LobbyAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'max_players', 'current_players', 'is_active', 'is_game_started', 'created_at')
    list_filter = ('is_active', 'is_game_started')
    date_hierarchy = 'created_at'
    list_display_links = ['name']
    raw_id_fields = ['creator']
    search_fields = ('name', 'creator__username')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'lobby', 'current_turn', 'is_finished', 'winner', 'created_at')
    list_filter = ('is_finished',)
    date_hierarchy = 'created_at'
    raw_id_fields = ['lobby', 'winner']
    search_fields = ('lobby__name', 'winner__username')


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'lobby', 'is_ready', 'joined_at')
    list_filter = ('is_ready',)
    date_hierarchy = 'joined_at'
    raw_id_fields = ['user', 'lobby']
    search_fields = ('user__username', 'lobby__name')
