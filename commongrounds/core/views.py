from django.shortcuts import render, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'core/index.html')

def explore(request):
    # Will add later
    return render(reqeust, 'core/index.html')

@login_required
def schedule(request):
    user_profile = get_object_or_404(Userprofile, user=request.user)
    venues_managed = Venue.objects.filter(venue_manager=user_profile)
    venue_schedules = Schedule.objects.filter(venue__in=venues_managed)
    
    services_provided = Service.objects.filter(provider=user_profile)
    service_schedules = Schedule.objects.filter(service__in=services_provided)
    
    consumer_schedules = Schedule.objects.filter(consumer=user_profile)    
   
    all_schedules = list(venue_schedules) + list(service_schedules) + list(consumer_schedules)
    
    context = {
        'schedules': all_schedules
    }
    
    return render(request, 'core/schedule.html', context)
