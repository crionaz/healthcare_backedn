from rest_framework import serializers
from .models import Shift, ShiftAssignment, ShiftSwapRequest
from staff.serializers import StaffMemberSerializer

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['id', 'name', 'start_time', 'end_time', 'break_duration', 'created_at', 'updated_at']

class ShiftAssignmentSerializer(serializers.ModelSerializer):
    staff_member_details = StaffMemberSerializer(source='staff_member', read_only=True)
    shift_details = ShiftSerializer(source='shift', read_only=True)
    
    class Meta:
        model = ShiftAssignment
        fields = ['id', 'staff_member', 'staff_member_details', 'shift', 'shift_details', 
                  'date', 'is_active', 'created_at', 'updated_at']
        
class ShiftSwapRequestSerializer(serializers.ModelSerializer):
    requester_details = serializers.SerializerMethodField()
    recipient_details = StaffMemberSerializer(source='recipient', read_only=True)
    requester_shift = ShiftSerializer(source='requester_assignment.shift', read_only=True)
    recipient_shift = ShiftSerializer(source='recipient_assignment.shift', read_only=True)
    
    class Meta:
        model = ShiftSwapRequest
        fields = ['id', 'requester_assignment', 'requester_details', 'recipient_assignment',
                  'recipient', 'recipient_details', 'status', 'reason', 'requester_shift',
                  'recipient_shift', 'created_at', 'updated_at']
        read_only_fields = ['status']
        
    def get_requester_details(self, obj):
        return {
            'id': obj.requester_assignment.staff_member.id,
            'name': obj.requester_assignment.staff_member.user.get_full_name(),
            'staff_id': obj.requester_assignment.staff_member.staff_id
        }
