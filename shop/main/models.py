import os
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254)
    image = models.ImageField(upload_to='profile_images', default='profile_pics/default.jpg')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Путь к изображению по относительному пути
        default_image_path = os.path.join(settings.MEDIA_ROOT, 'profile_images', 'default.jpg')

        try:
            img = Image.open(default_image_path)
            # Продолжайте операции с изображением...
        except FileNotFoundError:
            # Обработка ошибки, если файл не найден
            print(f"File not found: {default_image_path}")

class BuildingMaterials(models.Model):
    title = models.CharField(max_length=128, null=True, verbose_name='Название материала')
    description = models.TextField(max_length=256, null=True, verbose_name='Описание материала')
    image = models.ImageField(default='chto.png', upload_to='profile_pics')
    price = models.IntegerField(null=True, default=0, verbose_name='Цена')
    slug = models.SlugField(unique=True, null=True)  # Добавление поля slug
    available = models.BooleanField(default=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    likes = models.ManyToManyField(Profile, related_name='liked_materials', through='Like')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)  # Создание slug на основе заголовка, замените на нужное поле
        super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('main:post-detail', args=[self.id, self.slug])

    def __str__(self):
        return self.title

from PIL import Image

# Create your models here.


from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    post = models.ForeignKey(BuildingMaterials, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.author.username} on {self.post.title}'

class Like(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    material = models.ForeignKey(BuildingMaterials, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'material')