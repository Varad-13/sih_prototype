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
