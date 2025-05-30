from django.urls import path
# from . import views

urlpatterns = [
    # # Home and auth
    # path('', views.home, name='home'),
    # path('register/', views.register, name='register'),
    
    # # Staff management
    # path('staff/', views.staff_list, name='staff_list'),
    # path('staff/<str:staff_id>/', views.staff_detail, name='staff_detail'),
    # path('staff/<str:staff_id>/edit/', views.edit_staff, name='edit_staff'),
    # path('staff/<str:staff_id>/delete/', views.delete_staff, name='delete_staff'),
    # path('staff/<str:staff_id>/availability/', views.manage_availability, name='manage_availability'),
    
    # # Shift management
    # path('shifts/', views.shift_list, name='shift_list'),
    # path('shifts/create/', views.create_shift, name='create_shift'),
    # path('shifts/<int:shift_id>/edit/', views.edit_shift, name='edit_shift'),
    # path('shifts/<int:shift_id>/delete/', views.delete_shift, name='delete_shift'),
    
    # # Schedule management
    # path('schedule/', views.schedule_view, name='schedule_view'),
    # path('schedule/assign/', views.assign_shift, name='assign_shift'),
    # path('schedule/edit/<int:assignment_id>/', views.edit_assignment, name='edit_assignment'),
    # path('schedule/delete/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    
    # # Attendance
    # path('attendance/<int:assignment_id>/', views.mark_attendance, name='mark_attendance'),
    
    # # Availability
    # path('availability/delete/<int:availability_id>/', views.delete_availability, name='delete_availability'),
    
    # # Shift swaps
    # path('swap-requests/', views.swap_requests_list, name='swap_requests_list'),
    # path('swap-requests/<int:assignment_id>/create/', views.request_shift_swap, name='request_shift_swap'),
    # path('swap-requests/<int:request_id>/<str:action>/', views.handle_swap_request, name='handle_swap_request'),
]
