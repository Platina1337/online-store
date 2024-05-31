from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BuildingMaterials, Profile, Review, Category, Like


# Register your models here.
class Building(admin.ModelAdmin):
    list_display = [field.name for field in BuildingMaterials._meta.fields]
admin.site.register(BuildingMaterials, Building)
class ProfileModel(admin.ModelAdmin):
    list_display = [field.name for field in Profile._meta.fields]
admin.site.register(Profile, ProfileModel)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['author', 'content', 'created_at']

admin.site.register(Review, ReviewAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Category, CategoryAdmin)

class LikesAdmin(admin.ModelAdmin):
    list_display = ['user', 'material']

admin.site.register(Like, LikesAdmin)

