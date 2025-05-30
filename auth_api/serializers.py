from rest_framework import serializers
from django.contrib.auth.models import User
from staff.models import StaffMember

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(max_length=128, required=True, write_only=True)

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class TokenResponseSerializer(serializers.Serializer):
    """
    Serializer for token response
    """
    token = serializers.CharField()
    user_id = serializers.IntegerField()
    staff_id = serializers.IntegerField(required=False)
    is_staff = serializers.BooleanField()
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
