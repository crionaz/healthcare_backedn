from django.urls import path
from rest_framework import routers
from .views import ShiftViewSet, ShiftAssignmentViewSet, ShiftSwapRequestViewSet

router = routers.DefaultRouter()
router.register(r'shifts', ShiftViewSet)
router.register(r'assignments', ShiftAssignmentViewSet)
router.register(r'swap-requests', ShiftSwapRequestViewSet)

urlpatterns = router.urls
