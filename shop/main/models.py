from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import User
# Create your models here.



class BuildingMaterials(models.Model):
    title = models.CharField(max_length=128, null=True, verbose_name='Название материала')
    description = models.TextField(max_length=256, null=True, verbose_name='Описание материала')
    image = models.ImageField(default='chto.png', upload_to='profile_pics')
    pdf = models.FileField(validators=[FileExtensionValidator(['pdf'])], null=True, upload_to="luckych/uploads")
    price = models.IntegerField(null=True, default=0, verbose_name='Цена')

    def __str__(self):
        return self.title


from PIL import Image

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    email = models.CharField(max_length=128, null=True)


    def __str__(self):
        return f'{self.user.username} Profile'
    def save(self):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)