from django.contrib import admin

from .models import BuildingMaterials, Profile, Review


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