from django.shortcuts import redirect, render, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required


def index(request):
    if request.user.is_authenticated:
        try:
            user_profile = Userprofile.objects.get(user=request.user)
            context = {
                'userprofile': user_profile
            }
        except:
            print("User Profile not found")
            return redirect("/add_user")
    else:
        context = {}
    return render(request, 'core/index.html', context)

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
        'schedules': all_schedules,
        'userprofile': user_profile
    }
    return render(request, 'core/schedule.html', context)

@login_required
def user_creation(request):
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
