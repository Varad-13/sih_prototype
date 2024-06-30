from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Image(models.Model):
    file = models.ImageField(upload_to='images/')

class Userprofile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ForeignKey(Image, on_delete=models.CASCADE)
    bio = models.TextField()
    user_type = models.TextField()

class Timings(models.Model):
    daysofweek = models.IntegerField(default=1111111)
    starthour = models.TextField()
    endhour = models.TextField()

class State(models.Model):
    state_name = models.TextField()
    state_code = models.TextField()

class Locality(models.Model):
    postcode = models.IntegerField()
    place_name = models.TextField()
    state = models.ForeignKey(State, on_delete=models.CASCADE)

class ServiceTypes(models.Model):
    service_name = models.TextField()
    service_category = models.TextField()

class Service(models.Model):
    service_type = models.ForeignKey(ServiceTypes, on_delete=models.CASCADE)
    provider = models.ForeignKey(Userprofile, on_delete=models.CASCADE)
    description = models.TextField()
    timings = models.ForeignKey(Timings, on_delete=models.CASCADE)
    rate = models.FloatField()
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE)

class Venue(models.Model):
    venue_name = models.TextField()
    venue_images = models.ManyToManyField(Image)
    venue_manager = models.ForeignKey(Userprofile, on_delete=models.CASCADE)
    timings = models.ForeignKey(Timings, on_delete=models.CASCADE)
    description = models.TextField()
    rate = models.FloatField()
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE)

class Schedule(models.Model):
    consumer = models.ForeignKey(Userprofile, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    timing = models.ForeignKey(Timings, on_delete=models.CASCADE)
