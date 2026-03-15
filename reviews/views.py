from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Review


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user:
        return HttpResponseForbidden('لا يمكنك حذف هذا التقييم.')
    game_slug = review.game.slug
    review.delete()
    return redirect('game_detail', slug=game_slug)