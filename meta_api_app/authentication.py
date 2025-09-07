import datetime
import logging
import traceback

import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from meta_api_app.models import GameAccount

logger = logging.getLogger(__name__)

class MetaJWTUser:
    def __init__(self, username, day, month, random):
        self.username = username
        self.day = day
        self.month = month
        self.random = random
        self.is_authenticated = True

    def __str__(self):
        return self.username

class MetaJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication for Meta Online System.
    This replaces Django's default User authentication.
    """
    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        logger.debug(f"MetaJWTAuthentication auth: {auth}")

        if not auth or auth[0].lower() != b'bearer':
            # Return None to allow other authentication methods or permissions to handle
            return None
            
        if len(auth) == 1 or len(auth) > 2:
            msg = 'Invalid token header. No credentials provided.'
            raise AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
            logger.debug(f"MetaJWTAuthentication token: {token}")

            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'], options={'verify_iat': False})
                logger.debug(f"MetaJWTAuthentication payload decoded successfully")
            except Exception as e:
                logger.error(f"JWT decode error: {str(e)}")
                logger.error(traceback.format_exc())
                raise AuthenticationFailed(f'Token decode error: {str(e)}')

            logger.debug(f"MetaJWTAuthentication payload: {payload}")

            username = payload.get('username')
            day = payload.get('day')
            month = payload.get('month')
            random = payload.get('random')

            if not username or not day or not month or not random:
                raise AuthenticationFailed('Invalid token')

            logger.debug(f"MetaJWTAuthentication username: {username} day: {day} month: {month}")

            user = MetaJWTUser(username, day, month, random)

            return user, token
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            logger.error(traceback.format_exc())
            raise AuthenticationFailed(f'Authentication error: {str(e)}')

    @staticmethod
    def authenticate_refresh_token(refresh_token):
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])

            logger.debug(f"MetaJWTAuthentication payload: {payload}")

            if not payload.get('refresh'):
                raise AuthenticationFailed('Invalid refresh token')

            username = payload.get('username')
            day = payload.get('day')
            month = payload.get('month')
            random = payload.get('random')

            if not username or not day or not month or not random:
                raise AuthenticationFailed('Invalid token')

            return MetaJWTAuthentication._create_tokens(username, day, month, random)

        except Exception as e:
            raise AuthenticationFailed(f'Authentication error: {str(e)}')

    @staticmethod
    def authenticate_client(username, password, day, month, random):
        try:
            expected_username = MetaJWTAuthentication._calculate_username()
            expected_password = MetaJWTAuthentication._calculate_password(random)

            logger.debug(f"authenticate_client expected_username: {expected_username} expected_password: {expected_password}")

            today = timezone.now()
            expected_day = today.strftime('%A').lower()
            expected_month = today.strftime('%B').lower()

            if username != expected_username or password != expected_password or day != expected_day or month != expected_month:
                raise AuthenticationFailed('Invalid credentials')

            return MetaJWTAuthentication._create_tokens(username, day, month, random)

        except Exception as e:
            raise AuthenticationFailed(f'Authentication error: {str(e)}')

    @staticmethod
    def _calculate_username() -> str:
        today = timezone.now()
        day = today.strftime('%A').lower()
        month = today.strftime('%B').lower()
        result = []
        min_len = min(len(day), len(month))

        for i in range(min_len):
            if i < len(day):
                result.append(day[i])
            if i < len(month):
                result.append(month[i])

        return ''.join(result)

    @staticmethod
    def _calculate_password(random: str) -> str:
        if len(random) != 8 or not random.isdigit():
            raise ValueError("Input must be an 8-digit numeric string.")

        today = timezone.now()
        day_str = f"{today.day:02d}"
        month_str = f"{today.month:02d}"
        year_str = str(today.year)

        values = [
            int(random[0]) + int(day_str[0]),
            int(random[1]) + int(month_str[0]),
            int(random[2]) + int(year_str[0]),
            int(random[3]) + int(day_str[1]),
            int(random[4]) + int(month_str[1]),
            int(random[5]) + int(year_str[1]),
            int(random[6]) + int(year_str[2]),
            int(random[7]) + int(year_str[3]),
        ]

        result = ''.join(str(v % 10) for v in values)
        return result

    @staticmethod
    def _create_tokens(username: str, day: str, month: str, random: str) -> dict:
        # Get current time as timezone-aware datetime (respects Django's UTC setting)
        now = timezone.now()
        
        # JWT payload
        payload = {
            'username': username,
            'day': day,
            'month': month,
            'random': random,
            'user_id': username,
            'exp': int((now + datetime.timedelta(days=1)).timestamp()),
            'iat': int(now.timestamp()),
        }

        refresh_payload = {
            'username': username,
            'day': day,
            'month': month,
            'random': random,
            'user_id': username,
            'exp': int((now + datetime.timedelta(days=7)).timestamp()),
            'iat': int(now.timestamp()),
            'refresh': True
        }

        # Create access and refresh tokens
        access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')

        logger.debug(f"access_token: {access_token}")
        logger.debug(f"refresh_token: {refresh_token}")

        return {
            'access': access_token,
            'refresh': refresh_token,
        }