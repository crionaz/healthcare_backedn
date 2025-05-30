from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Role
from .serializers import RoleSerializer
from staff.models import StaffMember
from staff.serializers import StaffMemberSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing roles
    
    retrieve:
    Return a role instance.

    list:
    Return all roles.

    create:
    Create a new role.

    update:
    Update an existing role.

    partial_update:
    Update part of an existing role.

    delete:
    Delete a role.
    """
    queryset = Role.objects.all().order_by('name')
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        method='get',
        operation_description="Returns all staff members with the specified role",
        responses={200: 'List of staff members with this role'}
    )
    @action(detail=True, methods=['get'])
    def staff_members(self, request, pk=None):
        """
        Returns all staff members with the specified role
        """
        role = self.get_object()
        staff_members = StaffMember.objects.filter(role=role)
        serializer = StaffMemberSerializer(staff_members, many=True)
        return Response(serializer.data)
