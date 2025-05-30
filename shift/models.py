from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Shift(models.Model):
    """
    Model for defining different types of shifts
    """
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_duration = models.PositiveIntegerField(help_text="Break duration in minutes", default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Custom validation to ensure start_time is before end_time
        and that break_duration does not exceed the shift duration.
        """
        # For shifts spanning to next day (like night shifts), end time can be less than start time
        if self.start_time >= self.end_time and self.shift_type != 'night':
            raise ValidationError("Start time must be before end time, unless it's a night shift that extends to the next day.")
        
        # Calculate shift duration in minutes
        shift_duration = 0
        if self.shift_type == 'night' and self.end_time < self.start_time:
            # For night shifts that span to next day, add 24 hours to end_time
            shift_duration = ((self.end_time.hour + 24) * 60 + self.end_time.minute) - (self.start_time.hour * 60 + self.start_time.minute)
        else:
            shift_duration = (self.end_time.hour * 60 + self.end_time.minute) - (self.start_time.hour * 60 + self.start_time.minute)

        if self.break_duration >= shift_duration:
            raise ValidationError("Break duration must be less than the total shift duration.")
        
    def save(self, *args, **kwargs):
        """
        Override save method to ensure clean validation is called.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Shift"
        verbose_name_plural = "Shifts"
        ordering = ['start_time', 'end_time']
    
    def __str__(self):
        return f"{self.name} (Shift: {self.start_time}-{self.end_time})"

class ShiftAssignment(models.Model):
    """
    Model for assigning shifts to staff members
    """
    staff_member = models.ForeignKey('staff.StaffMember', on_delete=models.CASCADE, related_name='shift_assignments')
    shift = models.ForeignKey('shift.Shift', on_delete=models.CASCADE)
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
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class ShiftSwapRequest(models.Model):
    """
    Model for handling shift swap requests between staff members
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    requester_assignment = models.ForeignKey('shift.ShiftAssignment', on_delete=models.CASCADE, related_name='swap_requests_made')
    recipient_assignment = models.ForeignKey('shift.ShiftAssignment', on_delete=models.CASCADE, related_name='swap_requests_received', null=True, blank=True)
    recipient = models.ForeignKey('staff.StaffMember', on_delete=models.CASCADE, related_name='received_swap_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Custom validation to ensure that the requester and recipient are not the same
        and that the requester has an active shift assignment.
        """
        if self.requester_assignment.staff_member == self.recipient:
            raise ValidationError("Requester and recipient cannot be the same staff member.")
        
        if not self.requester_assignment.is_active:
            raise ValidationError("Requester must have an active shift assignment.")
        
    def save(self, *args, **kwargs):
        """
        Override save method to ensure clean validation is called.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Shift Swap Request"
        verbose_name_plural = "Shift Swap Requests"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Swap request from {self.requester_assignment.staff_member} to {self.recipient}"
