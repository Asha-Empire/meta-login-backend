from django.contrib import admin
from django import forms
from meta_api_app.models import GameAccount


class GameAccountAdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="The password must be entered in this field and will not be stored in clear text.")

    class Meta:
        model = GameAccount
        fields = '__all__'
        exclude = ['password_hash']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['password'].help_text = "Fill in if you want to change the password, otherwise leave it blank."

    def save(self, commit=True):
        game_account = super().save(commit=False)
        password = self.cleaned_data.get('password')

        if password:
            game_account.set_password(password)

        if commit:
            game_account.save()
        return game_account


class GameAccountAdmin(admin.ModelAdmin):
    form = GameAccountAdminForm
    list_display = [
        'username', 'display_name', 'character_name', 'email', 'level', 'experience_points', 
        'coins', 'gems', 'rank_tier', 'is_active', 'last_login_at'
    ]
    search_fields = ['username', 'email', 'display_name', 'character_name', 'guild_name']
    list_filter = [
        'is_active', 'level', 'rank_tier', 'created_at', 'last_login_at'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'last_login_at', 'total_playtime_minutes'
    ]
    
    # Custom list display formatting
    def get_list_display(self, request):
        return self.list_display
    
    # Add filters for numeric ranges
    list_filter = [
        'is_active', 
        'rank_tier',
        'level',
        ('created_at', admin.DateFieldListFilter),
        ('last_login_at', admin.DateFieldListFilter),
    ]

    def get_fieldsets(self, request, obj=None):
        """Customizes fieldsets based on whether object is being created or modified."""
        if not obj:
            # For creating a new user
            return [
                ('Account Information', {
                    'fields': ('username', 'email', 'password', 'is_active')
                }),
                ('Gaming Profile', {
                    'fields': ('display_name', 'character_name', 'level', 'experience_points'),
                    'classes': ('collapse',)
                }),
                ('Game Currency', {
                    'fields': ('coins', 'gems'),
                    'classes': ('collapse',)
                }),
                ('Player Stats', {
                    'fields': (
                        'health_points', 'max_health_points', 
                        'energy', 'max_energy'
                    ),
                    'classes': ('collapse',)
                }),
                ('Game Progress', {
                    'fields': (
                        'current_stage', 'achievements_unlocked', 'rank_tier'
                    ),
                    'classes': ('collapse',)
                }),
                ('Social Features', {
                    'fields': ('friends_count', 'guild_name'),
                    'classes': ('collapse',)
                }),
            ]
        else:
            # For editing an existing user
            return [
                ('Account Information', {
                    'fields': ('username', 'email', 'password', 'is_active')
                }),
                ('Gaming Profile', {
                    'fields': ('display_name', 'character_name', 'level', 'experience_points'),
                }),
                ('Game Currency', {
                    'fields': ('coins', 'gems'),
                }),
                ('Player Stats', {
                    'fields': (
                        'health_points', 'max_health_points', 
                        'energy', 'max_energy'
                    ),
                }),
                ('Game Progress', {
                    'fields': (
                        'current_stage', 'achievements_unlocked', 'rank_tier'
                    ),
                }),
                ('Gameplay Statistics', {
                    'fields': (
                        'total_playtime_minutes', 'games_played', 
                        'games_won', 'highest_score'
                    ),
                    'classes': ('collapse',)
                }),
                ('Social Features', {
                    'fields': ('friends_count', 'guild_name'),
                }),
                ('Timestamps', {
                    'fields': ('last_login_at', 'created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            ]

    def get_form(self, request, obj=None, **kwargs):
        """
        Use self.form as the form for creating/editing.
        """
        if 'fields' in kwargs:
            fields = kwargs.pop('fields')
            return super().get_form(request, obj, fields=fields, **kwargs)
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        """Ensure password is saved correctly through admin interface."""
        # 'password' from the form is already handled in form's save method
        # Just call the superclass method to save the model
        super().save_model(request, obj, form, change)
    
    # Custom actions for bulk operations
    actions = ['reset_energy', 'add_daily_bonus', 'deactivate_accounts']
    
    def reset_energy(self, request, queryset):
        """Reset energy to maximum for selected accounts."""
        updated = 0
        for account in queryset:
            account.restore_energy()
            updated += 1
        self.message_user(request, f'{updated} accounts had their energy restored.')
    reset_energy.short_description = "Reset energy to maximum for selected accounts"
    
    def add_daily_bonus(self, request, queryset):
        """Add daily bonus coins to selected accounts."""
        bonus_amount = 100  # Daily bonus amount
        updated = 0
        for account in queryset:
            account.add_coins(bonus_amount)
            updated += 1
        self.message_user(request, f'Added {bonus_amount} coins to {updated} accounts.')
    add_daily_bonus.short_description = "Add daily bonus (100 coins) to selected accounts"
    
    def deactivate_accounts(self, request, queryset):
        """Deactivate selected accounts."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} accounts were deactivated.')
    deactivate_accounts.short_description = "Deactivate selected accounts"