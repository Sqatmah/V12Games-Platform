from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import ProfileForm


def profile(request, username):
    user = get_object_or_404(User, username=username)
    reviews = user.review_set.select_related('game').order_by('-created_at')
    liked_games = user.liked_games.all()
    context = {
        'profile_user': user,
        'reviews': reviews,
        'liked_games': liked_games,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})