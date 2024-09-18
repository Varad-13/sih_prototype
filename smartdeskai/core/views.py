from django.shortcuts import redirect, render, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required

def index(request):
    return redirect('create_chat')

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
