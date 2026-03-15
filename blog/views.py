from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post


def post_list(request):
    posts = Post.objects.filter(published=True).order_by('-created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/list.html', {'page_obj': page_obj, 'posts': page_obj})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, published=True)
    return render(request, 'blog/detail.html', {'post': post})