from django.urls import path
from rest_framework import routers
from .views import DepartmentViewSet

router = routers.DefaultRouter()
router.register(r'', DepartmentViewSet)

urlpatterns = router.urls
