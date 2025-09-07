from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.utils import timezone


class GameAccount(models.Model):
    id = models.BigAutoField(primary_key=True)

    # Account Information
    username = models.CharField(max_length=150, unique=True, help_text="Username (can be an email address or a custom username).")
    email = models.EmailField(unique=True, help_text="The user's email address.")
    password_hash = models.CharField(max_length=128, help_text="Password hash value. Password is not stored in plain text.")
    is_active = models.BooleanField(default=True, help_text="Indicates whether the user is active or not.")
    
    # Gaming Profile
    display_name = models.CharField(max_length=100, blank=True, null=True, help_text="Display name shown to other players.")
    character_name = models.CharField(max_length=100, blank=True, null=True, help_text="In-game character display name.")
    level = models.PositiveIntegerField(default=1, help_text="Player's current level in the game.")
    experience_points = models.BigIntegerField(default=0, help_text="Total experience points earned by the player.")
    
    # Game Currency
    coins = models.BigIntegerField(default=0, help_text="Primary in-game currency (coins/gold).")
    gems = models.BigIntegerField(default=0, help_text="Premium in-game currency (gems/diamonds).")
    
    # Player Stats
    health_points = models.PositiveIntegerField(default=100, help_text="Current health/life points of the player.")
    max_health_points = models.PositiveIntegerField(default=100, help_text="Maximum health/life points of the player.")
    energy = models.PositiveIntegerField(default=100, help_text="Current energy points for gameplay activities.")
    max_energy = models.PositiveIntegerField(default=100, help_text="Maximum energy points the player can have.")
    
    # Game Progress
    current_stage = models.PositiveIntegerField(default=1, help_text="Current stage/level the player is on.")
    achievements_unlocked = models.PositiveIntegerField(default=0, help_text="Number of achievements unlocked by the player.")
    rank_tier = models.CharField(max_length=50, default='Bronze', help_text="Player's rank or tier in competitive gameplay.")
    
    # Gameplay Statistics
    total_playtime_minutes = models.BigIntegerField(default=0, help_text="Total time spent playing the game in minutes.")
    games_played = models.BigIntegerField(default=0, help_text="Total number of games/matches played.")
    games_won = models.BigIntegerField(default=0, help_text="Total number of games/matches won.")
    highest_score = models.BigIntegerField(default=0, help_text="Player's highest achieved score.")
    
    # Social Features
    friends_count = models.PositiveIntegerField(default=0, help_text="Number of friends the player has.")
    guild_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name of the guild/clan the player belongs to.")
    
    # Timestamps
    last_login_at = models.DateTimeField(null=True, blank=True, help_text="The date-time when the user last logged into the game.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The date-time the game account was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="The date-time the game account was updated.")

    class Meta:
        verbose_name = "Meta Game Account (GameAccount)"
        verbose_name_plural = "Meta Game Accounts (GameAccounts)"
        ordering = ['username']

    def __str__(self):
        return f"{self.username} (Level {self.level})"

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)
        self.password_changed_at = timezone.now()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)
    
    def update_last_login(self):
        """Update the last login timestamp to current time."""
        self.last_login_at = timezone.now()
        self.save(update_fields=['last_login_at'])
    
    def add_experience(self, exp_amount):
        """Add experience points and handle level up logic."""
        self.experience_points += exp_amount
        # Simple level calculation (can be customized based on game logic)
        new_level = (self.experience_points // 1000) + 1
        if new_level > self.level:
            self.level = new_level
        self.save(update_fields=['experience_points', 'level'])
    
    def add_coins(self, amount):
        """Add coins to the player's account."""
        self.coins += amount
        self.save(update_fields=['coins'])
    
    def spend_coins(self, amount):
        """Spend coins from the player's account if sufficient balance."""
        if self.coins >= amount:
            self.coins -= amount
            self.save(update_fields=['coins'])
            return True
        return False
    
    def restore_energy(self, amount=None):
        """Restore energy points to maximum or by specified amount."""
        if amount is None:
            self.energy = self.max_energy
        else:
            self.energy = min(self.energy + amount, self.max_energy)
        self.save(update_fields=['energy'])
    
    def spend_energy(self, amount):
        """Spend energy points if sufficient."""
        if self.energy >= amount:
            self.energy -= amount
            self.save(update_fields=['energy'])
            return True
        return False