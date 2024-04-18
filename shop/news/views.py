from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from .models import Video


# Create your views here.
class ViewNews(ListView):
    model = Video
    context_object_name = 'video_list'
    template_name = 'news/news.html'

def get_video(request, pk: int):
    _video = get_object_or_404(Video, id=pk)
    return render(request, "news/news.html", {"video": _video})
