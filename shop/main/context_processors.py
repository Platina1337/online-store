from .models import Profile

def followers_count(request):
    if request.user.is_authenticated:
        user_profile = Profile.objects.get(user=request.user)
        followers_count = user_profile.followers.count()
    else:
        followers_count = 0
    return {'followers_count': followers_count}