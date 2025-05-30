from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import (
    StaffMember,
    Shift,
    ShiftAssignment,
    StaffAvailability,
    ShiftSwapRequest,
    Attendance
)
from .forms import (
    UserRegistrationForm,
    StaffMemberForm,
    ShiftForm,
    ShiftAssignmentForm,
    StaffAvailabilityForm,
    ShiftSwapRequestForm,
    AttendanceForm
)

def home(request):
    """Homepage view"""
    return render(request, 'staff_management/home.html')

def register(request):
    """View for staff registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create StaffMember profile
            staff_member = StaffMember.objects.create(
                user=user,
                staff_id=form.cleaned_data.get('staff_id'),
                role=form.cleaned_data.get('role'),
                phone_number=form.cleaned_data.get('phone_number'),
                address=form.cleaned_data.get('address')
            )
            messages.success(request, f'Account created for {user.username}!')
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'staff_management/register.html', {'form': form})

@login_required
def staff_list(request):
    """View to list all staff members with filtering options"""
    staff_members = StaffMember.objects.all()
    
    # Handle search and filtering
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    
    if search_query:
        staff_members = staff_members.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(staff_id__icontains=search_query)
        )
    
    if role_filter:
        staff_members = staff_members.filter(role=role_filter)
    
    context = {
        'staff_members': staff_members,
        'search_query': search_query,
        'role_filter': role_filter,
        'roles': StaffMember.ROLE_CHOICES
    }
    
    return render(request, 'staff_management/staff_list.html', context)

@login_required
def staff_detail(request, staff_id):
    """View detailed information about a staff member"""
    staff_member = get_object_or_404(StaffMember, staff_id=staff_id)
    
    # Get upcoming shifts for this staff member
    upcoming_shifts = ShiftAssignment.objects.filter(
        staff_member=staff_member,
        date__gte=timezone.now().date(),
        is_active=True
    ).order_by('date')[:5]
    
    # Get attendance records
    attendance_records = Attendance.objects.filter(
        shift_assignment__staff_member=staff_member
    ).order_by('-shift_assignment__date')[:10]
    
    context = {
        'staff_member': staff_member,
        'upcoming_shifts': upcoming_shifts,
        'attendance_records': attendance_records
    }
    
    return render(request, 'staff_management/staff_detail.html', context)

@login_required
def edit_staff(request, staff_id):
    """View for editing staff information"""
    staff_member = get_object_or_404(StaffMember, staff_id=staff_id)
    
    if request.method == 'POST':
        form = StaffMemberForm(request.POST, instance=staff_member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff information updated successfully!')
            return redirect('staff_detail', staff_id=staff_id)
    else:
        form = StaffMemberForm(instance=staff_member)
    
    context = {
        'form': form,
        'staff_member': staff_member
    }
    
    return render(request, 'staff_management/edit_staff.html', context)

@login_required
def delete_staff(request, staff_id):
    """View for deleting staff members"""
    staff_member = get_object_or_404(StaffMember, staff_id=staff_id)
    
    if request.method == 'POST':
        # Delete the user (will cascade delete the staff member)
        staff_member.user.delete()
        messages.success(request, 'Staff member deleted successfully!')
        return redirect('staff_list')
    
    context = {'staff_member': staff_member}
    return render(request, 'staff_management/delete_staff.html', context)

@login_required
def shift_list(request):
    """View to list all shift types"""
    shifts = Shift.objects.all()
    context = {'shifts': shifts}
    return render(request, 'staff_management/shift_list.html', context)

@login_required
def create_shift(request):
    """View for creating new shift types"""
    if request.method == 'POST':
        form = ShiftForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New shift type created successfully!')
            return redirect('shift_list')
    else:
        form = ShiftForm()
    
    context = {'form': form}
    return render(request, 'staff_management/create_shift.html', context)

@login_required
def edit_shift(request, shift_id):
    """View for editing shift types"""
    shift = get_object_or_404(Shift, pk=shift_id)
    
    if request.method == 'POST':
        form = ShiftForm(request.POST, instance=shift)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shift updated successfully!')
            return redirect('shift_list')
    else:
        form = ShiftForm(instance=shift)
    
    context = {
        'form': form,
        'shift': shift
    }
    
    return render(request, 'staff_management/edit_shift.html', context)

@login_required
def delete_shift(request, shift_id):
    """View for deleting shift types"""
    shift = get_object_or_404(Shift, pk=shift_id)
    
    if request.method == 'POST':
        shift.delete()
        messages.success(request, 'Shift deleted successfully!')
        return redirect('shift_list')
    
    context = {'shift': shift}
    return render(request, 'staff_management/delete_shift.html', context)

@login_required
def schedule_view(request):
    """View for displaying the weekly schedule"""
    today = timezone.now().date()
    start_date = request.GET.get('start_date', today.strftime('%Y-%m-%d'))
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    except ValueError:
        start_date = today
    
    # Calculate the date range (7 days) for the schedule
    dates = [start_date + timedelta(days=i) for i in range(7)]
    
    # Get all shift assignments for the date range
    shift_assignments = ShiftAssignment.objects.filter(
        date__range=(dates[0], dates[6]),
        is_active=True
    ).select_related('staff_member', 'shift')
    
    # Organize assignments by date and shift
    schedule_data = {date: {} for date in dates}
    
    for assignment in shift_assignments:
        date = assignment.date
        if date not in schedule_data:
            continue
        
        if assignment.shift.id not in schedule_data[date]:
            schedule_data[date][assignment.shift.id] = []
        
        schedule_data[date][assignment.shift.id].append(assignment)
    
    # Get all shift types for display
    shifts = Shift.objects.all()
    
    context = {
        'schedule_data': schedule_data,
        'dates': dates,
        'shifts': shifts,
        'start_date': start_date,
        'prev_week': (start_date - timedelta(days=7)).strftime('%Y-%m-%d'),
        'next_week': (start_date + timedelta(days=7)).strftime('%Y-%m-%d'),
    }
    
    return render(request, 'staff_management/schedule.html', context)

@login_required
def assign_shift(request):
    """View for assigning shifts to staff members"""
    if request.method == 'POST':
        form = ShiftAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            
            try:
                # This will call the clean method to validate shift conflicts
                assignment.save()
                messages.success(request, 'Shift assigned successfully!')
                return redirect('schedule_view')
            except Exception as e:
                messages.error(request, f'Error assigning shift: {str(e)}')
    else:
        form = ShiftAssignmentForm()
    
    context = {'form': form}
    return render(request, 'staff_management/assign_shift.html', context)

@login_required
def edit_assignment(request, assignment_id):
    """View for editing shift assignments"""
    assignment = get_object_or_404(ShiftAssignment, pk=assignment_id)
    
    if request.method == 'POST':
        form = ShiftAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Shift assignment updated successfully!')
                return redirect('schedule_view')
            except Exception as e:
                messages.error(request, f'Error updating shift assignment: {str(e)}')
    else:
        form = ShiftAssignmentForm(instance=assignment)
    
    context = {
        'form': form,
        'assignment': assignment
    }
    
    return render(request, 'staff_management/edit_assignment.html', context)

@login_required
def delete_assignment(request, assignment_id):
    """View for deleting shift assignments"""
    assignment = get_object_or_404(ShiftAssignment, pk=assignment_id)
    
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Shift assignment deleted successfully!')
        return redirect('schedule_view')
    
    context = {'assignment': assignment}
    return render(request, 'staff_management/delete_assignment.html', context)

@login_required
def mark_attendance(request, assignment_id):
    """View for marking attendance for a shift"""
    assignment = get_object_or_404(ShiftAssignment, pk=assignment_id)
    
    # Try to get existing attendance record or create a new one
    try:
        attendance = Attendance.objects.get(shift_assignment=assignment)
    except Attendance.DoesNotExist:
        attendance = Attendance(shift_assignment=assignment)
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance marked successfully!')
            return redirect('schedule_view')
    else:
        form = AttendanceForm(instance=attendance)
    
    context = {
        'form': form,
        'assignment': assignment
    }
    
    return render(request, 'staff_management/mark_attendance.html', context)

@login_required
def manage_availability(request, staff_id):
    """View for managing staff availability preferences"""
    staff_member = get_object_or_404(StaffMember, staff_id=staff_id)
    
    if request.method == 'POST':
        form = StaffAvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.staff_member = staff_member
            
            # Check if availability already exists for this day
            existing = StaffAvailability.objects.filter(
                staff_member=staff_member,
                day_of_week=availability.day_of_week
            ).first()
            
            if existing:
                # Update existing availability
                existing.start_time = availability.start_time
                existing.end_time = availability.end_time
                existing.save()
                messages.success(request, 'Availability updated successfully!')
            else:
                # Create new availability
                availability.save()
                messages.success(request, 'Availability added successfully!')
                
            return redirect('manage_availability', staff_id=staff_id)
    else:
        form = StaffAvailabilityForm()
    
    # Get current availability for this staff member
    availabilities = StaffAvailability.objects.filter(staff_member=staff_member).order_by('day_of_week')
    
    context = {
        'form': form,
        'staff_member': staff_member,
        'availabilities': availabilities
    }
    
    return render(request, 'staff_management/manage_availability.html', context)

@login_required
def delete_availability(request, availability_id):
    """View for deleting staff availability"""
    availability = get_object_or_404(StaffAvailability, pk=availability_id)
    staff_id = availability.staff_member.staff_id
    
    if request.method == 'POST':
        availability.delete()
        messages.success(request, 'Availability deleted successfully!')
        return redirect('manage_availability', staff_id=staff_id)
    
    context = {'availability': availability}
    return render(request, 'staff_management/delete_availability.html', context)

@login_required
def request_shift_swap(request, assignment_id):
    """View for requesting shift swaps"""
    assignment = get_object_or_404(ShiftAssignment, pk=assignment_id)
    
    if request.method == 'POST':
        form = ShiftSwapRequestForm(request.POST)
        if form.is_valid():
            swap_request = form.save(commit=False)
            swap_request.requester_assignment = assignment
            swap_request.save()
            messages.success(request, 'Shift swap request submitted successfully!')
            return redirect('schedule_view')
    else:
        # Initialize with the current assignment
        form = ShiftSwapRequestForm(initial={'requester_assignment': assignment})
    
    context = {
        'form': form,
        'assignment': assignment
    }
    
    return render(request, 'staff_management/request_swap.html', context)

@login_required
def swap_requests_list(request):
    """View for listing all shift swap requests"""
    # Get requests where the current user is the recipient
    staff_member = request.user.staff_profile
    
    received_requests = ShiftSwapRequest.objects.filter(
        recipient=staff_member,
        status='pending'
    ).select_related('requester_assignment', 'recipient')
    
    # Get requests made by the current user
    made_requests = ShiftSwapRequest.objects.filter(
        requester_assignment__staff_member=staff_member
    ).select_related('requester_assignment', 'recipient')
    
    context = {
        'received_requests': received_requests,
        'made_requests': made_requests
    }
    
    return render(request, 'staff_management/swap_requests.html', context)

@login_required
def handle_swap_request(request, request_id, action):
    """View for approving or rejecting swap requests"""
    swap_request = get_object_or_404(ShiftSwapRequest, pk=request_id)
    
    if request.method == 'POST':
        if action == 'approve':
            # Find the recipient's shift on the same date
            recipient_assignment = ShiftAssignment.objects.filter(
                staff_member=swap_request.recipient,
                date=swap_request.requester_assignment.date
            ).first()
            
            if recipient_assignment:
                # Store the assignments
                requester_assignment = swap_request.requester_assignment
                
                # Update the shift assignments
                temp_shift = requester_assignment.shift
                requester_assignment.shift = recipient_assignment.shift
                recipient_assignment.shift = temp_shift
                
                # Save the changes
                requester_assignment.save()
                recipient_assignment.save()
                
                # Update the swap request
                swap_request.recipient_assignment = recipient_assignment
                swap_request.status = 'approved'
                swap_request.save()
                
                messages.success(request, 'Shift swap request approved and shifts swapped!')
            else:
                messages.error(request, 'You do not have a shift assigned on this date.')
                
        elif action == 'reject':
            swap_request.status = 'rejected'
            swap_request.save()
            messages.info(request, 'Shift swap request rejected.')
            
        return redirect('swap_requests_list')
    
    context = {
        'swap_request': swap_request,
        'action': action
    }
    
    return render(request, 'staff_management/handle_swap.html', context)
