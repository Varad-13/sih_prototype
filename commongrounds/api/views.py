from rest_framework import viewsets
from core.models import Userprofile, Service, Venue
from .serializers import UserprofileSerializer, ServiceSerializer, VenueSerializer

class UserprofileViewSet(viewsets.ModelViewSet):
    queryset = Userprofile.objects.all()
    serializer_class = UserprofileSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
