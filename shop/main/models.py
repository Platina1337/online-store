import os
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
# Create your models here.

from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название категории')
    description = models.TextField('Описание категории кратко ')
    url = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254, default='xxx@mail.com')
    image = models.ImageField(upload_to='profile_images', default='profile_pics/default.jpg')

    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=255, null=True)
    postal_code = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=100, null=True)


    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        # Вызов родительского метода save() для сохранения объекта
        super().save(*args, **kwargs)

        # Путь к изображению по относительному пути
        default_image_path = os.path.join(settings.MEDIA_ROOT, 'profile_images', 'default.jpg')

        # Проверяем существует ли файл по указанному пути
        if os.path.exists(default_image_path):
            try:
                # Открываем изображение
                with Image.open(default_image_path) as img:
                    # Выполняем какие-либо операции с изображением
                    # Например, можно изменить размер изображения
                    img.thumbnail((300, 300))  # Изменяем размер изображения до 300x300
                    img.save(self.image.path)  # Сохраняем измененное изображение в поле модели
            except FileNotFoundError:
                # Обработка ошибки, если файл не найден
                print(f"File not found: {default_image_path}")
        else:
            # Обработка случая, когда файл не существует по указанному пути
            print(f"Default image not found: {default_image_path}")


class BuildingMaterials(models.Model):
    title = models.CharField(max_length=128, null=True, verbose_name='Название материала')
    description = models.TextField(max_length=256, null=True, verbose_name='Описание материала')
    image = models.ImageField(default='chto.png', upload_to='profile_pics')
    price = models.IntegerField(null=True, default=0, verbose_name='Цена')
    slug = models.SlugField(unique=True, null=True)  # Добавление поля slug
    available = models.BooleanField(default=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    likes = models.ManyToManyField(Profile, related_name='liked_materials', through='Like')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='materials')

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


