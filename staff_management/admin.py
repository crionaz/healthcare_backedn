from django.contrib import admin
from .models import (
    StaffMember, 
    Shift, 
    ShiftAssignment,
    StaffAvailability,
    ShiftSwapRequest,
    Attendance
)

# Admin Page Details like Site name, Header, Index Title
admin.site.site_header = "Healthcare Staff Management"
admin.site.site_title = "Healthcare Staff Admin"
admin.site.index_title = "Welcome to the Healthcare Staff Management Admin Portal"


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'get_full_name', 'role', 'phone_number')
    list_filter = ('role',)
    search_fields = ('staff_id', 'user__first_name', 'user__last_name', 'phone_number')
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'shift_type', 'start_time', 'end_time', 'roles')
    list_filter = ('shift_type',)
    search_fields = ('name',)

@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ('staff_member', 'shift', 'date', 'is_active')
    list_filter = ('date', 'is_active', 'shift')
    search_fields = ('staff_member__user__first_name', 'staff_member__user__last_name')
    date_hierarchy = 'date'

@admin.register(StaffAvailability)
class StaffAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('staff_member', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week',)

@admin.register(ShiftSwapRequest)
class ShiftSwapRequestAdmin(admin.ModelAdmin):
    list_display = ('requester_assignment', 'recipient', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('requester_assignment__staff_member__user__first_name', 
                    'requester_assignment__staff_member__user__last_name',
                    'recipient__user__first_name',
                    'recipient__user__last_name')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('shift_assignment', 'status', 'check_in_time', 'check_out_time')
    list_filter = ('status', 'check_in_time')
    search_fields = ('shift_assignment__staff_member__user__first_name',
                    'shift_assignment__staff_member__user__last_name')
