import logging

from rest_framework import serializers
from meta_api_app.models import GameAccount
from django.contrib.auth.hashers import check_password

logger = logging.getLogger(__name__)

class GameAccountRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for game account registration."""
    password = serializers.CharField(write_only=True, min_length=6, help_text="Password must be at least 6 characters long.")
    password_confirm = serializers.CharField(write_only=True, help_text="Password confirmation field.")

    class Meta:
        model = GameAccount
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'display_name'
        ]
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }

    def validate_email(self, value):
        """Validate that email is unique."""
        if GameAccount.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_username(self, value):
        """Validate that username is unique."""
        if GameAccount.objects.filter(username=value).exists():
            raise serializers.ValidationError("An account with this username already exists.")
        return value

    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        """Create a new game account with hashed password."""
        validated_data.pop('password_confirm')  # Remove password confirmation
        password = validated_data.pop('password')
        
        # Create the account
        game_account = GameAccount.objects.create(**validated_data)
        game_account.set_password(password)
        game_account.save()
        
        return game_account


class GameAccountLoginSerializer(serializers.Serializer):
    """Serializer for game account login."""
    username = serializers.CharField(help_text="Username or email address.")
    password = serializers.CharField(write_only=True, help_text="Account password.")

    def validate(self, attrs):
        """Validate login credentials."""
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError("Both username and password are required.")

        # Try to find account by username or email
        try:
            # First try username
            account = GameAccount.objects.get(username=username)
        except GameAccount.DoesNotExist:
            try:
                # Then try email
                account = GameAccount.objects.get(email=username)
            except GameAccount.DoesNotExist:
                raise serializers.ValidationError("Invalid login credentials.")

        logger.debug(f"GameAccountLoginSerializer validate for '{account}'")

        # Check if account is active
        if not account.is_active:
            raise serializers.ValidationError("Account is inactive.")

        # Check password
        if not account.check_password(password):
            raise serializers.ValidationError("Invalid login credentials.")

        attrs['account'] = account
        logger.debug(f"GameAccountLoginSerializer return {attrs}")
        return attrs


class GameAccountResponseSerializer(serializers.ModelSerializer):
    """Serializer for game account response data (excluding timestamps)."""
    
    class Meta:
        model = GameAccount
        exclude = ['password_hash', 'created_at', 'updated_at']


class GameAccountProfileSerializer(serializers.ModelSerializer):
    """Serializer for game account profile updates."""
    
    class Meta:
        model = GameAccount
        fields = [
            'character_name', 'level', 'experience_points', 'coins', 'gems',
            'health_points', 'max_health_points', 'energy', 'max_energy',
            'current_stage', 'achievements_unlocked', 'rank_tier',
            'total_playtime_minutes', 'games_played', 'games_won', 
            'highest_score', 'friends_count', 'guild_name'
        ]
        read_only_fields = [
            'level', 'total_playtime_minutes', 'games_played', 
            'games_won', 'highest_score'
        ] 