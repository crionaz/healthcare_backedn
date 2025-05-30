from rest_framework import serializers
from django.contrib.auth.models import User
from .models import StaffMember

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['username']

class StaffMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    department_name = serializers.StringRelatedField(source='department')
    role_name = serializers.StringRelatedField(source='role')
    
    class Meta:
        model = StaffMember
        fields = ['id', 'staff_id', 'user', 'department', 'department_name', 'role', 'role_name', 
                  'phone_number', 'address', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(
            username=user_data.get('username'),
            email=user_data.get('email'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            password='password123'  # Default password, should be changed by user
        )
        return StaffMember.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        
        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.email = user_data.get('email', user.email)
            user.save()
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance
