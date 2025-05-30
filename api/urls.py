from django.urls import path, include

urlpatterns = [
    # Auth endpoints
    path('auth/', include('auth_api.urls')),
    
    # API resources
    path('staff/', include('staff.urls')),
    path('roles/', include('role.urls')),
    path('shifts/', include('shift.urls')),
    path('attendance/', include('attendance.urls')),
    path('departments/', include('department.urls')),
    
    path('api-auth/', include('rest_framework.urls')),
]
