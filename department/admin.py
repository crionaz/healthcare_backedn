from django.contrib import admin
from .models import Department
from unfold.admin import ModelAdmin

# Register your models here.
@admin.register(Department)
class DepartmentAdmin(ModelAdmin):
    list_display = ('name', 'description_truncated', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)
    
    def description_truncated(self, obj):
        if obj.description and len(obj.description) > 50:
            return obj.description[:50] + '...'
        return obj.description
    description_truncated.short_description = 'Description'