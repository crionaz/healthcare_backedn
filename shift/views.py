from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Shift, ShiftAssignment, ShiftSwapRequest
from .serializers import ShiftSerializer, ShiftAssignmentSerializer, ShiftSwapRequestSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ShiftViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing shifts
    
    retrieve:
    Return a shift instance.

    list:
    Return all shifts.

    create:
    Create a new shift.

    update:
    Update an existing shift.

    partial_update:
    Update part of an existing shift.

    delete:
    Delete a shift.
    """
    queryset = Shift.objects.all().order_by('name')
    serializer_class = ShiftSerializer
    permission_classes = [permissions.IsAuthenticated]

class ShiftAssignmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing shift assignments
    
    retrieve:
    Return a shift assignment instance.

    list:
    Return all shift assignments, optionally filtered by date range, staff member, or shift.

    create:
    Create a new shift assignment.

    update:
    Update an existing shift assignment.

    partial_update:
    Update part of an existing shift assignment.

    delete:
    Delete a shift assignment.
    """
    queryset = ShiftAssignment.objects.all().select_related('staff_member', 'shift')
    serializer_class = ShiftAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ShiftAssignment.objects.all().select_related('staff_member', 'staff_member__role', 
                                                               'staff_member__department', 'shift')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Filter by staff member
        staff_id = self.request.query_params.get('staff_id')
        if staff_id:
            queryset = queryset.filter(staff_member__staff_id=staff_id)
            
        # Filter by role
        role_id = self.request.query_params.get('role_id')
        if role_id:
            queryset = queryset.filter(staff_member__role_id=role_id)
            
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def schedule(self, request):
        """
        Returns shift schedule for a date range, grouped by date
        """
        # Get date range, default to current week
        today = timezone.now().date()
        start_date = request.query_params.get('start_date', today.strftime('%Y-%m-%d'))
        days = int(request.query_params.get('days', 7))
        
        # Convert start_date to date object if it's a string
        if isinstance(start_date, str):
            import datetime
            try:
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
                
        end_date = start_date + timedelta(days=days-1)
        
        # Query shift assignments in the date range
        assignments = ShiftAssignment.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            is_active=True
        ).select_related('staff_member', 'staff_member__role', 'shift')
        
        # Organize by date
        schedule = {}
        dates = []
        current_date = start_date
        
        while current_date <= end_date:
            dates.append(current_date.strftime('%Y-%m-%d'))
            schedule[current_date.strftime('%Y-%m-%d')] = []
            current_date += timedelta(days=1)
        
        # Group assignments by date
        for assignment in assignments:
            date_str = assignment.date.strftime('%Y-%m-%d')
            if date_str in schedule:
                serializer = ShiftAssignmentSerializer(assignment)
                schedule[date_str].append(serializer.data)
        
        return Response({
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'dates': dates,
            'schedule': schedule
        })

class ShiftSwapRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing shift swap requests
    """
    queryset = ShiftSwapRequest.objects.all().select_related(
        'requester_assignment__staff_member', 'requester_assignment__shift',
        'recipient_assignment__staff_member', 'recipient_assignment__shift',
        'recipient'
    )
    serializer_class = ShiftSwapRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by staff member (either requester or recipient)
        staff_id = self.request.query_params.get('staff_id')
        if staff_id:
            queryset = queryset.filter(
                Q(requester_assignment__staff_member__staff_id=staff_id) | 
                Q(recipient__staff_id=staff_id)
            )
            
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(requester_assignment__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(requester_assignment__date__lte=end_date)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a shift swap request
        """
        swap_request = self.get_object()
        
        if swap_request.status != 'pending':
            return Response({'error': 'This request has already been processed'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Find recipient's shift assignment for the same date
        recipient_assignment = ShiftAssignment.objects.filter(
            staff_member=swap_request.recipient,
            date=swap_request.requester_assignment.date
        ).first()
        
        if not recipient_assignment:
            return Response({'error': 'Recipient does not have a shift assignment on this date'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Store the assignments
        requester_assignment = swap_request.requester_assignment
        
        # Update the shift assignments
        temp_shift = requester_assignment.shift
        requester_assignment.shift = recipient_assignment.shift
        recipient_assignment.shift = temp_shift
        
        # Save the changes
        requester_assignment.save()
        recipient_assignment.save()
        
        # Update the swap request
        swap_request.recipient_assignment = recipient_assignment
        swap_request.status = 'approved'
        swap_request.save()
        
        serializer = self.get_serializer(swap_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a shift swap request
        """
        swap_request = self.get_object()
        
        if swap_request.status != 'pending':
            return Response({'error': 'This request has already been processed'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        swap_request.status = 'rejected'
        swap_request.save()
        
        serializer = self.get_serializer(swap_request)
        return Response(serializer.data)
