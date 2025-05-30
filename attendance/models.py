from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from staff.models import StaffMember
from shift.models import ShiftAssignment

class LeaveRequest(models.Model):
    """
    Model for managing staff leave requests
    """
    LEAVE_TYPE_CHOICES = (
        ('sick', 'Sick Leave'),
        ('vacation', 'Vacation'),
        ('personal', 'Personal Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('bereavement', 'Bereavement'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    
    staff_member = models.ForeignKey('staff.StaffMember', on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.staff_member.user.get_full_name()} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"
    
    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date must be before or equal to end date.")
            
        overlapping_leaves = LeaveRequest.objects.filter(
            staff_member=self.staff_member,
            status='approved',
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        ).exclude(pk=self.pk)
        
        if overlapping_leaves.exists():
            raise ValidationError("There is already an approved leave that overlaps with this period.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Update conflicting shift assignments if leave is approved
        if self.status == 'approved':
            ShiftAssignment.objects.filter(
                staff_member=self.staff_member,
                date__range=(self.start_date, self.end_date),
                is_active=True
            ).update(is_active=False)


class Attendance(models.Model):
    """
    Model for tracking staff attendance
    """
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
        ('leave', 'On Leave'),
    )
    
    staff_member = models.ForeignKey('staff.StaffMember', on_delete=models.CASCADE, related_name='attendance_records')
    shift_assignment = models.ForeignKey('shift.ShiftAssignment', on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('staff_member', 'date', 'shift_assignment')
        ordering = ['-date', 'staff_member']
    
    def __str__(self):
        return f"{self.staff_member.user.get_full_name()} - {self.shift_assignment.shift.name} - {self.date} - {self.get_status_display()}"
    
    def clean(self):
        if self.check_in_time and self.check_out_time and self.check_in_time > self.check_out_time:
            raise ValidationError("Check-in time must be before check-out time.")
        
        if self.shift_assignment and self.date != self.shift_assignment.date:
            raise ValidationError("Attendance date must match the shift assignment date.")
    
    def save(self, *args, **kwargs):
        import datetime
        self.full_clean()
        
        # Auto-determine status if check-in exists
        if self.check_in_time and not self.status == 'leave':
            # Get shift start time as datetime for comparison
            shift_start = datetime.datetime.combine(
                self.date,
                self.shift_assignment.shift.start_time
            )
            
            # If more than 10 minutes late
            if self.check_in_time > (shift_start + datetime.timedelta(minutes=10)):
                self.status = 'late'
            else:
                self.status = 'present'
            
        super().save(*args, **kwargs)

