from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class StaffMember(models.Model):
    """
    Model for staff members including personal information and role
    """
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('technician', 'Technician'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    staff_id = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()} ({self.staff_id})"

class Shift(models.Model):
    """
    Model for defining different types of shifts
    """
    SHIFT_TYPE_CHOICES = (
        ('morning', 'Morning Shift'),
        ('evening', 'Evening Shift'),
        ('night', 'Night Shift'),
    )

    name = models.CharField(max_length=100)
    shift_type = models.CharField(max_length=20, choices=SHIFT_TYPE_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_duration = models.PositiveIntegerField(help_text="Break duration in minutes", default=30)
    roles = models.CharField(max_length=100, help_text="Comma separated roles that can be assigned to this shift")
    
    def __str__(self):
        return f"{self.name} ({self.get_shift_type_display()}: {self.start_time}-{self.end_time})"

class ShiftAssignment(models.Model):
    """
    Model for assigning shifts to staff members
    """
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='shift_assignments')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('staff_member', 'date')
        ordering = ['date', 'shift__start_time']

    def __str__(self):
        return f"{self.staff_member.user.get_full_name()} - {self.shift.name} on {self.date}"
    
    def clean(self):
        """
        Check for shift conflicts
        """
        # Check if staff member has another shift assignment on the same day
        existing_assignments = ShiftAssignment.objects.filter(
            staff_member=self.staff_member,
            date=self.date,
            is_active=True
        ).exclude(pk=self.pk)
        
        if existing_assignments.exists():
            raise ValidationError("Staff member already has a shift assignment on this date.")
        
        # Check if staff member role is allowed for this shift
        staff_role = self.staff_member.role
        allowed_roles = [role.strip().lower() for role in self.shift.roles.split(',')]
        
        if staff_role not in allowed_roles:
            raise ValidationError(f"Staff member with role '{staff_role}' cannot be assigned to this shift.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class StaffAvailability(models.Model):
    """
    Model for tracking staff availability preferences
    """
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.PositiveSmallIntegerField(choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        unique_together = ('staff_member', 'day_of_week')
    
    def __str__(self):
        return f"{self.staff_member.user.get_full_name()} - {self.get_day_of_week_display()} ({self.start_time}-{self.end_time})"

class ShiftSwapRequest(models.Model):
    """
    Model for handling shift swap requests between staff members
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    requester_assignment = models.ForeignKey(ShiftAssignment, on_delete=models.CASCADE, related_name='swap_requests_made')
    recipient_assignment = models.ForeignKey(ShiftAssignment, on_delete=models.CASCADE, related_name='swap_requests_received', null=True, blank=True)
    recipient = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='received_swap_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Swap request from {self.requester_assignment.staff_member} to {self.recipient}"

class Attendance(models.Model):
    """
    Model for tracking attendance of staff for shifts
    """
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    )
    
    shift_assignment = models.OneToOneField(ShiftAssignment, on_delete=models.CASCADE, related_name='attendance')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.shift_assignment.staff_member} - {self.status} on {self.shift_assignment.date}"
