from rest_framework import serializers
from .models import Department

class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Department model
    """
    staff_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'staff_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_staff_count(self, obj):
        """
        Get the number of staff members in this department
        """
        return obj.staffmember_set.count() if hasattr(obj, 'staffmember_set') else 0
