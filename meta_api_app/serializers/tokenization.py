from rest_framework import serializers


class MetaTokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    day = serializers.CharField(required=True)
    month = serializers.CharField(required=True)
    random = serializers.CharField(required=True)

class MetaTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)