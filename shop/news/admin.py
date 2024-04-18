from django.contrib import admin

from .models import Video


# Register your models here.
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'image', 'file', 'create_at']

admin.site.register(Video, VideoAdmin)