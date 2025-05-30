from django.contrib import admin
from .models import StaffMember
from unfold.admin import ModelAdmin

# Register your models here.
class StaffMemberAdmin(ModelAdmin):
    list_display = ('staff_id', 'get_full_name', 'department', 'role', 'phone_number')
    list_filter = ('department', 'role')
    search_fields = ('user__first_name', 'user__last_name', 'staff_id', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'staff_id', 'phone_number', 'address')
        }),
        ('Professional Information', {
            'fields': ('department', 'role')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

admin.site.register(StaffMember, StaffMemberAdmin)