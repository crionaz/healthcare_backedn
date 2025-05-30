from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import StaffMember
from .serializers import StaffMemberSerializer
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class StaffMemberViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing staff members
    
    retrieve:
    Return a staff member instance.

    list:
    Return all staff members, optionally filtered by role or department.

    create:
    Create a new staff member.

    update:
    Update an existing staff member.

    partial_update:
    Update part of an existing staff member.

    delete:
    Delete a staff member.
    """
    queryset = StaffMember.objects.all()
    serializer_class = StaffMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    
    def get_queryset(self):
        """
        Optionally filters staff members by role or department
        """
        queryset = StaffMember.objects.all().select_related('user', 'role', 'department')
        
        # Filter by role if provided
        role_id = self.request.query_params.get('role')
        if role_id:
            queryset = queryset.filter(role_id=role_id)
            
        # Filter by department if provided
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
            
        return queryset
    
    @swagger_auto_schema(
        method='get',
        operation_description="Returns all shift assignments for a specific staff member",
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Filter by start date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="Filter by end date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        ]
    )
    @action(detail=True, methods=['get'])
    def shifts(self, request, pk=None):
        """
        Returns all shift assignments for a specific staff member
        """
        staff_member = self.get_object()
        from shift.serializers import ShiftAssignmentSerializer
        from shift.models import ShiftAssignment
        
        # Get shift assignments with optional date filtering
        assignments = ShiftAssignment.objects.filter(staff_member=staff_member)
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            assignments = assignments.filter(date__gte=start_date)
        if end_date:
            assignments = assignments.filter(date__lte=end_date)
            
        serializer = ShiftAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Returns attendance records for a specific staff member",
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Filter by start date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="Filter by end date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        ]
    )
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """
        Returns attendance records for a specific staff member
        """
        staff_member = self.get_object()
        from attendance.serializers import AttendanceSerializer
        from attendance.models import Attendance
        
        # Get attendance records with optional date filtering
        attendance_records = Attendance.objects.filter(staff_member=staff_member)
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            attendance_records = attendance_records.filter(date__gte=start_date)
        if end_date:
            attendance_records = attendance_records.filter(date__lte=end_date)
            
        serializer = AttendanceSerializer(attendance_records, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Returns leave requests for a specific staff member",
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status (pending, approved, rejected)", type=openapi.TYPE_STRING, enum=["pending", "approved", "rejected"]),
        ]
    )
    @action(detail=True, methods=['get'])
    def leave_requests(self, request, pk=None):
        """
        Returns leave requests for a specific staff member
        """
        staff_member = self.get_object()
        from attendance.serializers import LeaveRequestSerializer
        from attendance.models import LeaveRequest
        
        # Get leave requests with optional status filtering
        leave_requests = LeaveRequest.objects.filter(staff_member=staff_member)
        
        # Filter by status if provided
        status = request.query_params.get('status')
        if status:
            leave_requests = leave_requests.filter(status=status)
            
        serializer = LeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get current user profile if associated with a staff member",
        responses={200: 'Current staff member profile', 404: 'No staff member found for current user'}
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Returns the staff member profile associated with the current authenticated user
        """
        try:
            staff_member = StaffMember.objects.get(user=request.user)
            serializer = self.get_serializer(staff_member)
            return Response(serializer.data)
        except StaffMember.DoesNotExist:
            return Response(
                {'error': 'No staff member profile found for the current user'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    

