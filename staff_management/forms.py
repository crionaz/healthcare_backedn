from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    StaffMember, 
    Shift, 
    ShiftAssignment,
    StaffAvailability,
    ShiftSwapRequest,
    Attendance
)

class UserRegistrationForm(UserCreationForm):
    """Form for user registration with additional fields for staff member"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    staff_id = forms.CharField(max_length=50, required=True)
    role = forms.ChoiceField(choices=StaffMember.ROLE_CHOICES, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class StaffMemberForm(forms.ModelForm):
    """Form for updating staff members"""
    class Meta:
        model = StaffMember
        fields = ('role', 'phone_number', 'address')

class ShiftForm(forms.ModelForm):
    """Form for creating and updating shifts"""
    roles = forms.CharField(
        help_text="Enter comma-separated roles (e.g., doctor,nurse,technician)",
        required=True
    )
    
    class Meta:
        model = Shift
        fields = ('name', 'shift_type', 'start_time', 'end_time', 'break_duration', 'roles')

class ShiftAssignmentForm(forms.ModelForm):
    """Form for assigning shifts to staff members"""
    class Meta:
        model = ShiftAssignment
        fields = ('staff_member', 'shift', 'date')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter staff members based on active status
        self.fields['staff_member'].queryset = StaffMember.objects.all().order_by('user__first_name')

class StaffAvailabilityForm(forms.ModelForm):
    """Form for staff availability preferences"""
    class Meta:
        model = StaffAvailability
        fields = ('day_of_week', 'start_time', 'end_time')
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class ShiftSwapRequestForm(forms.ModelForm):
    """Form for creating shift swap requests"""
    class Meta:
        model = ShiftSwapRequest
        fields = ('requester_assignment', 'recipient', 'reason')
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

class AttendanceForm(forms.ModelForm):
    """Form for marking attendance"""
    class Meta:
        model = Attendance
        fields = ('status', 'check_in_time', 'check_out_time', 'comments')
        widgets = {
            'check_in_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'check_out_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }
