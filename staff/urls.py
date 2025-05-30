from django.urls import path
from rest_framework import routers
from .views import StaffMemberViewSet

router = routers.DefaultRouter()
router.register(r'', StaffMemberViewSet)

urlpatterns = router.urls
