from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import LandSeeker

@receiver(user_logged_in)
def user_logged_in_redirect(sender, request, user, **kwargs):
    # Check if the logged-in user is a land seeker
    if LandSeeker.objects.filter(user=user).exists():
        return HttpResponseRedirect(reverse('landseeker_profile'))
