from django.contrib import admin
from .models import Image, Userprofile, Timings, State, Locality, ServiceTypes, Service, Venue, Schedule

admin.site.register(Image)
admin.site.register(Userprofile)
admin.site.register(Timings)
admin.site.register(State)
admin.site.register(Locality)
admin.site.register(ServiceTypes)
admin.site.register(Service)
admin.site.register(Venue)
admin.site.register(Schedule)
