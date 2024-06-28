from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserprofileViewSet, ServiceViewSet, VenueViewSet

router = DefaultRouter()
router.register(r'userprofiles', UserprofileViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'venues', VenueViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
