from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LeaveRequest, Attendance
from .serializers import LeaveRequestSerializer, AttendanceSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing leave requests
    
    retrieve:
    Return a leave request instance.

    list:
    Return all leave requests, optionally filtered by staff ID or status.

    create:
    Create a new leave request.

    update:
    Update an existing leave request.

    partial_update:
    Update part of an existing leave request.

    delete:
    Delete a leave request.
    """
    queryset = LeaveRequest.objects.all().select_related('staff_member', 'approved_by')
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by staff member
        staff_id = self.request.query_params.get('staff_id')
        if staff_id:
            queryset = queryset.filter(staff_member__staff_id=staff_id)
            
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(
                Q(start_date__gte=start_date) | Q(end_date__gte=start_date)
            )
        if end_date:
            queryset = queryset.filter(
                Q(start_date__lte=end_date) | Q(end_date__lte=end_date)
            )
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a leave request
        """
        leave_request = self.get_object()
        
        if leave_request.status != 'pending':
            return Response({'error': 'This request has already been processed'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        leave_request.status = 'approved'
        leave_request.approved_by = request.user
        leave_request.save()
        
        # Update conflicting shift assignments
        from shift.models import ShiftAssignment
        ShiftAssignment.objects.filter(
            staff_member=leave_request.staff_member,
            date__range=(leave_request.start_date, leave_request.end_date),
            is_active=True
        ).update(is_active=False)
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a leave request
        """
        leave_request = self.get_object()
        
        if leave_request.status != 'pending':
            return Response({'error': 'This request has already been processed'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        leave_request.status = 'rejected'
        leave_request.approved_by = request.user
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a leave request
        """
        leave_request = self.get_object()
        
        if leave_request.status not in ['pending', 'approved']:
            return Response({'error': 'This request cannot be cancelled'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        leave_request.status = 'cancelled'
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing attendance
    """
    queryset = Attendance.objects.all().select_related('staff_member', 'shift_assignment')
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by staff member
        staff_id = self.request.query_params.get('staff_id')
        if staff_id:
            queryset = queryset.filter(staff_member__staff_id=staff_id)
            
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        return queryset
    
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """
        Mark attendance check-in for a staff member
        """
        staff_id = request.data.get('staff_id')
        shift_assignment_id = request.data.get('shift_assignment_id')
        
        if not staff_id or not shift_assignment_id:
            return Response({'error': 'Staff ID and shift assignment ID are required'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        from staff.models import StaffMember
        from shift.models import ShiftAssignment
        
        staff_member = get_object_or_404(StaffMember, staff_id=staff_id)
        shift_assignment = get_object_or_404(ShiftAssignment, id=shift_assignment_id)
        
        if shift_assignment.staff_member != staff_member:
            return Response({'error': 'This shift is not assigned to this staff member'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create attendance record
        attendance, created = Attendance.objects.get_or_create(
            staff_member=staff_member,
            shift_assignment=shift_assignment,
            date=shift_assignment.date,
            defaults={'status': 'present', 'check_in_time': timezone.now()}
        )
        
        if not created:
            if attendance.check_in_time:
                return Response({'error': 'You have already checked in for this shift'}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            attendance.check_in_time = timezone.now()
            attendance.save()
        
        serializer = self.get_serializer(attendance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def check_out(self, request):
        """
        Mark attendance check-out for a staff member
        """
        staff_id = request.data.get('staff_id')
        shift_assignment_id = request.data.get('shift_assignment_id')
        
        if not staff_id or not shift_assignment_id:
            return Response({'error': 'Staff ID and shift assignment ID are required'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        from staff.models import StaffMember
        from shift.models import ShiftAssignment
        
        staff_member = get_object_or_404(StaffMember, staff_id=staff_id)
        shift_assignment = get_object_or_404(ShiftAssignment, id=shift_assignment_id)
        
        if shift_assignment.staff_member != staff_member:
            return Response({'error': 'This shift is not assigned to this staff member'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        try:
            attendance = Attendance.objects.get(
                staff_member=staff_member,
                shift_assignment=shift_assignment,
                date=shift_assignment.date
            )
        except Attendance.DoesNotExist:
            return Response({'error': 'You need to check in before checking out'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        if not attendance.check_in_time:
            return Response({'error': 'You need to check in before checking out'}, 
                           status=status.HTTP_400_BAD_REQUEST)
            
        if attendance.check_out_time:
            return Response({'error': 'You have already checked out for this shift'}, 
                           status=status.HTTP_400_BAD_REQUEST)
            
        attendance.check_out_time = timezone.now()
        attendance.save()
        
        serializer = self.get_serializer(attendance)
        return Response(serializer.data)
