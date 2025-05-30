from django.urls import path
from rest_framework import routers
from .views import RoleViewSet

router = routers.DefaultRouter()
router.register(r'', RoleViewSet)

urlpatterns = router.urls
