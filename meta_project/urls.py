from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from meta_api_app.views import MetaTokenObtainView, MetaTokenRefreshView
# Import game account views
from meta_api_app.views.game_account import (
    GameAccountRegisterView, GameAccountLoginView,
    GameAccountProfileView, GameAccountLogoutView  # New class-based views
)

# Health check endpoint for monitoring
def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    # Health check endpoint
    path('health/', health_check, name='health-check'),

    # Meta Token endpoints
    path('api/token/', MetaTokenObtainView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', MetaTokenRefreshView.as_view(), name='token_refresh'),

    # Game Account Authentication endpoints
    path('api/game/register/', GameAccountRegisterView.as_view(), name='game_register'),
    path('api/game/login/', GameAccountLoginView.as_view(), name='game_login'),
    path('api/game/logout/', GameAccountLogoutView.as_view(), name='game_logout'),
    path('api/game/profile/', GameAccountProfileView.as_view(), name='game_profile'),

    # Django Admin (renamed to avoid confusion)
    path('meta-admin/', admin.site.urls),
]
