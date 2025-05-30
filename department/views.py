from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Department
from .serializers import DepartmentSerializer
from staff.serializers import StaffMemberSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing departments
    
    retrieve:
    Return a department instance.

    list:
    Return all departments.

    create:
    Create a new department.

    update:
    Update an existing department.

    partial_update:
    Update part of an existing department.

    delete:
    Delete a department.
    """
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        method='get',
        operation_description="Returns all staff members in a specific department",
        responses={200: 'List of staff members in this department'}
    )
    @action(detail=True, methods=['get'])
    def staff_members(self, request, pk=None):
        """
        Returns all staff members in a specific department
        """
        department = self.get_object()
        staff_members = department.staffmember_set.all()
        serializer = StaffMemberSerializer(staff_members, many=True)
        return Response(serializer.data)
