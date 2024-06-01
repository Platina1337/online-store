import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.urls import reverse
from django.utils.text import slugify
from PIL import Image
from django.contrib.auth import get_user_model
# Импортируем наш пользовательский метод
from .utils import *
class User(AbstractUser):
    role = models.BooleanField(default=False)

    class Meta:
        swappable = 'AUTH_USER_MODEL'
        db_table = 'main_user'
class Contact(models.Model):
    user_from = models.ForeignKey('Profile', related_name='rel_from_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey('Profile', related_name='rel_to_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user_from', 'user_to'),)

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254, default='xxx@mail.com')
    image = models.ImageField(upload_to='profile_images', default='profile_pics/default.jpg')
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=255, null=True)
    postal_code = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=100, null=True)
    passport_number = models.CharField(max_length=6, null=True)
    passport_series = models.CharField(max_length=4, null=True)

    following = models.ManyToManyField('self', through='Contact', symmetrical=False, related_name='followers')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        default_image_path = os.path.join(settings.MEDIA_ROOT, 'profile_images', 'default.jpg')

        if os.path.exists(default_image_path):
            try:
                with Image.open(default_image_path) as img:
                    img.thumbnail((300, 300))
                    img.save(self.image.path)
            except FileNotFoundError:
                print(f"File not found: {default_image_path}")
        else:
            print(f"Default image not found: {default_image_path}")
class Category(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название категории')
    description = models.TextField('Описание категории кратко ')
    url = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class BuildingMaterials(models.Model):
    title = models.CharField(max_length=128, null=True, verbose_name='Название материала')
    description = models.TextField(max_length=256, null=True, verbose_name='Описание материала')
    image = models.ImageField(default='chto.png', upload_to='profile_pics')
    price = models.IntegerField(null=True, default=0, verbose_name='Цена')
    slug = models.SlugField(unique=True, null=True)
    available = models.BooleanField(default=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    likes = models.ManyToManyField(Profile, related_name='liked_materials', through='Like')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='materials')
    views = models.PositiveIntegerField(default=0, verbose_name='Количество просмотров')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('main:post-detail', args=[self.id, self.slug])

    def __str__(self):
        return self.title

class Review(models.Model):
    post = models.ForeignKey(BuildingMaterials, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.author.username} on {self.post.title}'

class Like(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    material = models.ForeignKey(BuildingMaterials, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'material')
