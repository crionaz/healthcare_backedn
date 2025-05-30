from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class StaffMember(models.Model):
    """
    Model for staff members including personal information and role
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    staff_id = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey('department.Department', on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey('role.Role', on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role.name} ({self.staff_id})"
    
    def clean(self):
        """
        Custom validation to ensure staff_id is unique across all staff members.
        """
        if StaffMember.objects.filter(staff_id=self.staff_id).exclude(pk=self.pk).exists():
            raise ValidationError({'staff_id': 'Staff ID must be unique.'})
        
        if not self.staff_id.isalnum():
            raise ValidationError({'staff_id': 'Staff ID must be alphanumeric.'})
        
        if len(self.staff_id) < 5:
            raise ValidationError({'staff_id': 'Staff ID must be at least 5 characters long.'})
        
    def save(self, *args, **kwargs):
        """
        Override save method to ensure clean validation is called.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"
        ordering = ['user__first_name', 'user__last_name']

