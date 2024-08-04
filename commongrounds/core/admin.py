from django.contrib import admin
from .models import Image, Userprofile, Timings, Locality, ServiceTypes, Service, Venue, Schedule, Address

admin.site.register(Image)
admin.site.register(Userprofile)
admin.site.register(Timings)
admin.site.register(Locality)
admin.site.register(Address)
admin.site.register(ServiceTypes)
admin.site.register(Service)
admin.site.register(Venue)
admin.site.register(Schedule)
