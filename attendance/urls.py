from django.urls import path
from rest_framework import routers
from .views import LeaveRequestViewSet, AttendanceViewSet

router = routers.DefaultRouter()
router.register(r'leave-requests', LeaveRequestViewSet)
router.register(r'records', AttendanceViewSet)

urlpatterns = router.urls
