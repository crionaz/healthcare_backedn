from rest_framework import serializers
from .models import LeaveRequest, Attendance
from staff.serializers import StaffMemberSerializer
from shift.serializers import ShiftAssignmentSerializer

class LeaveRequestSerializer(serializers.ModelSerializer):
    staff_member_details = StaffMemberSerializer(source='staff_member', read_only=True)
    approved_by_name = serializers.SerializerMethodField()
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = ['id', 'staff_member', 'staff_member_details', 'leave_type', 'leave_type_display',
                  'start_date', 'end_date', 'reason', 'status', 'status_display', 'approved_by', 
                  'approved_by_name', 'created_at', 'updated_at']
        read_only_fields = ['approved_by', 'status']
        
    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return obj.approved_by.get_full_name()
        return None

class AttendanceSerializer(serializers.ModelSerializer):
    staff_member_details = StaffMemberSerializer(source='staff_member', read_only=True)
    shift_assignment_details = ShiftAssignmentSerializer(source='shift_assignment', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'staff_member', 'staff_member_details', 'shift_assignment', 'shift_assignment_details',
                  'date', 'status', 'status_display', 'check_in_time', 'check_out_time', 
                  'notes', 'created_at', 'updated_at']
