from django.contrib import admin
from .models import LeaveRequest, Attendance
from unfold.admin import ModelAdmin


@admin.register(LeaveRequest)
class LeaveRequestAdmin(ModelAdmin):
    list_display = ('staff_member', 'leave_type_display', 'start_date', 'end_date', 'status_display', 'approved_by')
    list_filter = ('status', 'leave_type', 'start_date')
    search_fields = ('staff_member__user__first_name', 'staff_member__user__last_name', 'reason')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Staff Information', {'fields': ('staff_member',)}),
        ('Leave Details', {'fields': ('leave_type', 'start_date', 'end_date', 'reason')}),
        ('Status', {'fields': ('status', 'approved_by')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def leave_type_display(self, obj):
        return obj.get_leave_type_display()
    leave_type_display.short_description = 'Leave Type'
    
    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = 'Status'
    
    def approve_leaves(self, request, queryset):
        queryset.update(status='approved', approved_by=request.user)
    approve_leaves.short_description = "Approve selected leave requests"
    
    def reject_leaves(self, request, queryset):
        queryset.update(status='rejected', approved_by=request.user)
    reject_leaves.short_description = "Reject selected leave requests"
    
    actions = ['approve_leaves', 'reject_leaves']

@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    list_display = ('staff_member', 'date', 'shift_assignment', 'status_display', 'check_in_time', 'check_out_time')
    list_filter = ('status', 'date')
    search_fields = ('staff_member__user__first_name', 'staff_member__user__last_name', 'notes')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Staff and Shift', {'fields': ('staff_member', 'shift_assignment', 'date')}),
        ('Attendance Details', {'fields': ('status', 'check_in_time', 'check_out_time', 'notes')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = 'Status'
    
    def mark_as_present(self, request, queryset):
        queryset.update(status='present')
    mark_as_present.short_description = "Mark selected records as present"
    
    def mark_as_absent(self, request, queryset):
        queryset.update(status='absent')
    mark_as_absent.short_description = "Mark selected records as absent"
    
    actions = ['mark_as_present', 'mark_as_absent']
