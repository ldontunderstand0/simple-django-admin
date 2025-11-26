from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import User, Lobby, Game, Player


class HasWinnerFilter(admin.SimpleListFilter):
    title = 'Есть ли победитель'
    parameter_name = 'has_winner'

    def lookups(self, request, model_admin):
        return ('Yes', 'Есть победитель'), ('No', 'Нет победителя')

    def queryset(self, request, queryset):
        match self.value():
            case 'Yes':
                return queryset.filter(winner__isnull=False)
            case 'No':
                return queryset.filter(winner__isnull=True)
        return queryset


class HasLobbyFilter(admin.SimpleListFilter):
    title = 'Привязан к лобби'
    parameter_name = 'has_lobby'

    def lookups(self, request, model_admin):
        return ('Yes', 'Да'), ('No', 'Нет')

    def queryset(self, request, queryset):
        match self.value():
            case 'Yes':
                return queryset.filter(lobby__isnull=False)
            case 'No':
                return queryset.filter(lobby__isnull=True)
        return queryset


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ('username', 'email', 'password', 'is_active', 'is_online')
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
    list_display = (
        'id', 'name', 'creator', 'max_players', 'current_players', 'games', 'is_active', 'is_game_started', 'created_at'
    )
    list_filter = ('is_active', 'is_game_started')
    date_hierarchy = 'created_at'
    list_display_links = ['id']
    raw_id_fields = ['creator']
    search_fields = ('name', 'creator__username')

    @admin.display()
    def games(self, obj):
        return obj.games.count()

    games.short_description = 'Количество игр'


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'lobby', 'current_turn', 'is_finished', 'winner', 'created_at')
    list_filter = ('is_finished', 'lobby', HasWinnerFilter)
    date_hierarchy = 'created_at'
    raw_id_fields = ['lobby', 'winner']
    search_fields = ('lobby__name', 'winner__username')


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'lobby', 'is_ready', 'joined_at')
    list_filter = ('is_ready', HasLobbyFilter)
    date_hierarchy = 'joined_at'
    raw_id_fields = ['user', 'lobby']
    search_fields = ('user__username', 'lobby__name')
