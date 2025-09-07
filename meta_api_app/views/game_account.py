import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from meta_api_app.authentication import MetaJWTAuthentication
from meta_api_app.serializers.game_account import (
    GameAccountRegistrationSerializer,
    GameAccountLoginSerializer,
    GameAccountResponseSerializer
)

logger = logging.getLogger(__name__)


class GameAccountRegisterView(APIView):
    """
    Register a new game account with Bearer token authentication.
    """
    authentication_classes = [MetaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Register a new game account.
        
        Expected payload:
        {
            "username": "player123",
            "email": "player@example.com", 
            "password": "securepassword",
            "password_confirm": "securepassword",
            "display_name": "PlayerOne" (optional)
        }
        """
        serializer = GameAccountRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Create the account
                game_account = serializer.save()
                
                return Response({
                    'success': True,
                    'message': 'Account created successfully.',
                    'username': game_account.username
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'success': False,
                    'message': 'Account creation failed. Please try again.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': False,
            'message': 'Registration failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class GameAccountLoginView(APIView):
    """
    Login with game account credentials with Bearer token authentication.
    """
    authentication_classes = [MetaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Login with game account credentials.
        
        Expected payload:
        {
            "username": "player123",  // Can be username or email
            "password": "securepassword"
        }
        """
        try:
            serializer = GameAccountLoginSerializer(data=request.data)

            logger.debug(f"GameAccountLoginSerializer return {serializer}")
        
            if serializer.is_valid():
                # Get the validated account
                account = serializer.validated_data['account']
                
                # Update last login time
                account.update_last_login()
                
                # Serialize account data (excluding timestamps)
                account_serializer = GameAccountResponseSerializer(account)
                
                return Response({
                    'success': True,
                    'message': 'Login successful.',
                    'account': account_serializer.data
                }, status=status.HTTP_200_OK)
        
            return Response({
                'success': False,
                'message': 'Login failed. Invalid credentials.',
                'errors': serializer.errors
            }, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({
                'success': False,
                'message': 'Login failed. Please try again.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GameAccountProfileView(APIView):
    """
    Get current user's profile information.
    """
    authentication_classes = [MetaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get current user's profile information.
        Requires authentication token.
        """
        try:
            # Get the authenticated GameAccount
            account = request.user
            
            serializer = GameAccountResponseSerializer(account)
            
            return Response({
                'success': True,
                'account': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to retrieve profile.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GameAccountLogoutView(APIView):
    """
    Logout user.
    """
    authentication_classes = [MetaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Logout user by blacklisting the refresh token.
        """
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = MetaJWTAuthentication(refresh_token)
                token.blacklist()
                
            return Response({
                'success': True,
                'message': 'Logout successful.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Logout failed.',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
