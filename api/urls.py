from django.urls import path, include

urlpatterns = [
    path('staff/', include('staff.urls')),
    path('roles/', include('role.urls')),
    path('shifts/', include('shift.urls')),
    path('attendance/', include('attendance.urls')),
    path('departments/', include('department.urls')),
    
    # DRF browsable API login/logout views
    path('api-auth/', include('rest_framework.urls')),
]
