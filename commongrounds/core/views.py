from django.shortcuts import redirect, render, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required

def index(request):
    context = {}
    if request.user.is_authenticated:
        user_profile = Userprofile.objects.filter(user=request.user).first()
        if user_profile:
            context['userprofile'] = user_profile
        else:
            return redirect('/add_user')
    return render(request, 'core/index.html', context)

def people(request):
    services = Service.objects.select_related('provider').all()
    context = {}
    if request.user.is_authenticated:
        user_profile = Userprofile.objects.filter(user=request.user).first()
        if user_profile:
            context['userprofile'] = user_profile
        else:
            return redirect('/add_user')
        
    users_with_services = {}
    for service in services:
        if service.provider not in users_with_services:
            users_with_services[service.provider] = []
        users_with_services[service.provider].append(service) 

    context["users_with_services"] = users_with_services

    return render(request, 'core/people.html', context)

@login_required
def schedule(request):
    context = {}
    if request.user.is_authenticated:
        user_profile = Userprofile.objects.filter(user=request.user).first()
        if user_profile:
            context['userprofile'] = user_profile

            venues_managed = Venue.objects.filter(venue_manager=user_profile)
            venue_schedules = Schedule.objects.filter(venue__in=venues_managed)
            services_provided = Service.objects.filter(provider=user_profile)
            service_schedules = Schedule.objects.filter(service__in=services_provided)
            consumer_schedules = Schedule.objects.filter(consumer=user_profile)    

            context['schedules'] = {
                'venue_schedules': venue_schedules,
                'service_schedules': service_schedules,
                'consumer_schedules': consumer_schedules,
            }
        else:
            return redirect('/add_user')

    return render(request, 'core/schedule.html', context)

@login_required
def user_creation(request):
    if Userprofile.objects.filter(user=request.user).exists():
        return redirect('index')  
    if request.method == 'POST':
        name = request.POST.get('name')
        bio = request.POST.get('bio')
        profile_image_file = request.FILES.get('profile_image')

        # Save the image
        image = Image(file=profile_image_file)
        image.save()

        # Create and save the user profile
        user_profile = Userprofile(
            name=name,
            user=request.user,
            profile_image=image,
            bio=bio,
        )
        user_profile.save()

        return redirect('index')
    else:
        return render(request, 'core/user_onboarding.html')
