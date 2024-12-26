from .messages import MESSAGES
from .models import Profile

def get_or_create_profile(username):
    profile, created = Profile.objects.get_or_create(username=username)
    return profile

def get_user_state(profile):
    return profile.state

def set_user_state(profile, state):
    profile.state = state
    profile.save()

def get_message(profile, key):
    language = profile.language if profile.language in MESSAGES else 'ru'
    return MESSAGES[language].get(key, MESSAGES['ru'].get(key, ''))
