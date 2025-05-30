from django.contrib import admin
from .models import Shift, ShiftAssignment, ShiftSwapRequest
from unfold.admin import ModelAdmin

# Register your models here.
@admin.register(Shift)
class ShiftAdmin(ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'break_duration')
    list_filter = ('start_time', 'end_time')
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Time Details', {
            'fields': ('start_time', 'end_time', 'break_duration')
        }),
    )

@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(ModelAdmin):
    list_display = ('staff_member', 'shift', 'date', 'is_active')
    list_filter = ('is_active', 'date', 'shift')
    search_fields = ('staff_member__user__first_name', 'staff_member__user__last_name')
    date_hierarchy = 'date'
    autocomplete_fields = ['staff_member', 'shift']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('staff_member__user', 'shift')

@admin.register(ShiftSwapRequest)
class ShiftSwapRequestAdmin(ModelAdmin):
    list_display = ('requester_info', 'recipient', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('requester_assignment__staff_member__user__username', 'recipient__user__username')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('requester_assignment', 'recipient_assignment', 'recipient')
    
    def requester_info(self, obj):
        return f"{obj.requester_assignment.staff_member} - {obj.requester_assignment.shift}"
    requester_info.short_description = 'Requester'
    
    fieldsets = (
        ('Request Details', {
            'fields': ('requester_assignment', 'recipient', 'recipient_assignment', 'status')
        }),
        ('Additional Information', {
            'fields': ('reason', 'created_at', 'updated_at')
        }),
    )