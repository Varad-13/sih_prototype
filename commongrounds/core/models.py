from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Image(models.Model):
    file = models.ImageField(upload_to='images/')

class Userprofile(models.Model):
    name = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ForeignKey(Image, on_delete=models.CASCADE)
    bio = models.TextField()
    isConsultant = models.BooleanField(default=False)
    isVenueManager = models.BooleanField(default=False)

class Timings(models.Model):
    daysofweek = models.IntegerField(default=1111111)
    starthour = models.TimeField()
    endhour = models.TimeField()

class Locality(models.Model):
    postcode = models.IntegerField(unique=True, primary_key=True)
    place_name = models.TextField()
    state_name = models.TextField()
    state_code = models.TextField()

class Address(models.Model):
    address_line_1 = models.TextField()
    address_line_2 = models.TextField()
    street_name = models.TextField()
    Locality = models.ForeignKey(Locality, on_delete=models.CASCADE)
    google_embed_link = models.URLField()

class ServiceTypes(models.Model):
    service_name = models.TextField()
    service_category = models.TextField()

class Service(models.Model):
    service_type = models.ForeignKey(ServiceTypes, on_delete=models.CASCADE, related_name='services')
    provider = models.ForeignKey(Userprofile, on_delete=models.CASCADE)
    description = models.TextField()
    timings = models.ForeignKey(Timings, on_delete=models.CASCADE)
    rate = models.FloatField()
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE)

class Venue(models.Model):
    venue_name = models.TextField()
    venue_images = models.ManyToManyField(Image)
    venue_manager = models.ForeignKey(Userprofile, on_delete=models.CASCADE, related_name='venues')
    timings = models.ForeignKey(Timings, on_delete=models.CASCADE)
    description = models.TextField()
    rate = models.FloatField()
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

class Schedule(models.Model):
    consumer = models.ForeignKey(Userprofile, on_delete=models.CASCADE, related_name='events')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='events')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='events')
    day = models.DateTimeField()
