import logging

import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from meta_api_app.authentication import MetaJWTAuthentication
from meta_api_app.serializers.tokenization import MetaTokenObtainSerializer, MetaTokenRefreshSerializer

logger = logging.getLogger(__name__)

class MetaTokenObtainView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MetaTokenObtainSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            day = serializer.validated_data.get('day')
            month = serializer.validated_data.get('month')
            random = serializer.validated_data.get('random')

            logger.debug(f"POST token obtain username:{username} password:{password}")

            tokens = MetaJWTAuthentication.authenticate_client(username, password, day, month, random)
            return Response(tokens, status=status.HTTP_200_OK)
        except ValidationError as e:
            logger.error(f"Validation error during login: {str(e)}")
            return Response(
                {"error": "Invalid data", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return Response(
                {"error": "Authentication failed", "detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )


class MetaTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MetaTokenRefreshSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            refresh_token = serializer.validated_data.get('refresh')

            try:
                return Response(MetaJWTAuthentication.authenticate_refresh_token(refresh_token), status=status.HTTP_200_OK)

            except jwt.ExpiredSignatureError:
                return Response(
                    {"error": "Refresh token has expired"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            except jwt.InvalidTokenError:
                return Response(
                    {"error": "Invalid refresh token"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        except ValidationError as e:
            logger.error(f"Validation error during token refresh: {str(e)}")
            return Response(
                {"error": "Invalid data", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error during token refresh: {str(e)}")
            return Response(
                {"error": "Token refresh failed", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
