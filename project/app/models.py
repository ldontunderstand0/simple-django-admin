from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='Логин')
    email = models.EmailField(max_length=100, unique=True, db_index=True, verbose_name='Электронная почта')
    password = models.CharField(max_length=255, verbose_name='Пароль')
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

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            player = Player(user=self)
            player.save()


class Lobby(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    creator = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name="lobbies", verbose_name='Создатель'
    )
    max_players = models.IntegerField(default=2, verbose_name='Максимум игроков')
    current_players = models.IntegerField(default=0, verbose_name='Сейчас игроков')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    is_game_started = models.BooleanField(default=False, verbose_name='Игра в процессе')
    created_at = models.DateTimeField(auto_now_add=timezone.now, verbose_name='Создано')

    def __str__(self):
        return f"Lobby(id={self.pk})"

    class Meta:
        verbose_name = "Лобби"
        verbose_name_plural = "Лобби"
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        if self.pk is None:
            creator = Player.objects.get(user=self.creator)
            if creator.lobby:
                raise ValidationError('Создатель уже находится в лобби')
            return
        lobby = Lobby.objects.get(pk=self.pk)
        if lobby.creator != self.creator:
            old_creator = Player.objects.get(user=lobby.creator)
            new_creator = Player.objects.get(user=self.creator)
            if new_creator.lobby:
                raise ValidationError('Создатель уже находится в лобби')
            new_creator.lobby = self
            new_creator.save()
            old_creator.lobby = None
            old_creator.save()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            creator = Player.objects.get(user=self.creator)
            creator.lobby = self
            creator.save()


class Game(models.Model):
    lobby = models.ForeignKey('Lobby', on_delete=models.CASCADE, related_name="games", verbose_name='Лобби')
    current_turn = models.IntegerField(default=0, verbose_name='Текущий ход')
    is_finished = models.BooleanField(default=False, verbose_name='Игра закончена')
    winner = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True, related_name="won_games", verbose_name='Победитель'
    )
    created_at = models.DateTimeField(auto_now_add=timezone.now, verbose_name='Создана')

    def __str__(self):
        return f"Game(lobby_id={self.lobby.pk})"

    class Meta:
        verbose_name = "Игра"
        verbose_name_plural = "Игры"
        ordering = ['-created_at']


class Player(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name="players", verbose_name='Пользователь')
    lobby = models.ForeignKey(
        'Lobby', on_delete=models.SET_NULL, related_name="players", verbose_name='Лобби', null=True, blank=True
    )
    is_ready = models.BooleanField(default=False, verbose_name='Готов к игре')
    joined_at = models.DateTimeField(auto_now=timezone.now, verbose_name='Присоединился')

    def __str__(self):
        return f"Player(user_id={self.user.pk})"

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"
        ordering = ['-joined_at']

    def clean(self):
        super().clean()
        if self.lobby:
            lobby = Lobby.objects.get(pk=self.lobby.pk)
            if lobby.current_players + 1 > self.lobby.max_players:
                raise ValidationError('Лобби полностью заполнено')

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
            return
        old_lobby = Player.objects.get(pk=self.pk).lobby
        if old_lobby:
            old_lobby.current_players -= 1
            old_lobby.save()
        new_lobby = self.lobby
        if new_lobby and new_lobby != old_lobby:
            new_lobby.current_players += 1
            new_lobby.save()
        super().save(*args, **kwargs)
