from django.db import models
from django.utils import timezone


class User(models.Model):
    username = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='Логин')
    email = models.EmailField(max_length=100, unique=True, db_index=True, verbose_name='Электронная почта')
    hashed_password = models.CharField(max_length=255, verbose_name='Хешированный пароль')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=timezone.now, verbose_name='Создан')
    last_seen = models.DateTimeField(auto_now=timezone.now, verbose_name='Последний вход')
    is_online = models.BooleanField(default=False, verbose_name='Онлайн')

    def __str__(self):
        return f"{self.username}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-created_at']


class Lobby(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    creator = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name="lobbies", verbose_name='Создатель'
    )
    max_players = models.IntegerField(default=2, verbose_name='Максимум игроков')
    current_players = models.IntegerField(default=1, verbose_name='Сейчас игроков')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    is_game_started = models.BooleanField(default=False, verbose_name='Игра началась')
    created_at = models.DateTimeField(auto_now_add=timezone.now, verbose_name='Создано')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Лобби"
        verbose_name_plural = "Лобби"
        ordering = ['-created_at']


class Game(models.Model):
    lobby = models.ForeignKey('Lobby', on_delete=models.CASCADE, related_name="games", verbose_name='Лобби')
    current_turn = models.IntegerField(default=0, verbose_name='Текущий ход')
    is_finished = models.BooleanField(default=False, verbose_name='Игра закончена')
    winner = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True, related_name="won_games", verbose_name='Победитель'
    )
    created_at = models.DateTimeField(auto_now_add=timezone.now, verbose_name='Создана')

    def __str__(self):
        return f"{self.lobby_id}"

    class Meta:
        verbose_name = "Игра"
        verbose_name_plural = "Игры"
        ordering = ['-created_at']


class Player(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="players", verbose_name='Пользователь')
    lobby = models.ForeignKey('Lobby', on_delete=models.CASCADE, related_name="players", verbose_name='Лобби')
    is_ready = models.BooleanField(default=False, verbose_name='Готов к игре')
    joined_at = models.DateTimeField(auto_now_add=timezone.now, verbose_name='Присоединился')

    def __str__(self):
        return f"{self.user_id}"

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"
        ordering = ['-joined_at']
