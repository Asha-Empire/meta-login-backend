from django.contrib import admin

from meta_api_app.admin.game_account import GameAccountAdmin
from meta_api_app.models import GameAccount

admin.site.site_header = "Meta Backend Database Admin Panel"
admin.site.site_title = "Meta Backend Database Admin Panel"
admin.site.index_title = "Welcome to Meta Backend Database Admin Panel"

admin.site.register(GameAccount, GameAccountAdmin)
