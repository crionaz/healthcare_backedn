from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UserLoginSerializer, TokenResponseSerializer
from staff.models import StaffMember
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class LoginAPIView(APIView):
    """
    API view for user login
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response('Login successful', TokenResponseSerializer),
            401: 'Authentication failed'
        }
    )
    def post(self, request):
        """
        Login endpoint that returns an authentication token
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                
                # Check if user is a staff member
                is_staff_member = False
                staff_id = None
                
                try:
                    staff_member = StaffMember.objects.get(user=user)
                    is_staff_member = True
                    staff_id = staff_member.id
                except StaffMember.DoesNotExist:
                    pass
                    
                return Response({
                    'token': token.key,
                    'user_id': user.id,
                    'staff_id': staff_id,
                    'is_staff': user.is_staff or is_staff_member,
                    'username': user.username,
                    'email': user.email or '',
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or ''
                }, status=status.HTTP_200_OK)
            
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    """
    API view for user logout
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        responses={200: 'Logged out successfully'}
    )
    def post(self, request):
        """
        Logout endpoint that invalidates the current token
        """
        if request.auth:
            request.auth.delete()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        
        return Response({"detail": "No authentication token found."}, status=status.HTTP_400_BAD_REQUEST)
