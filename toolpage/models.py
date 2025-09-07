from django.db import models

# Create your models here.

class BackgroundImage(models.Model):
    POSITION_CHOICES = [
        ('left', '左'),
        ('right', '右'),
        ('normal', '一般'),
    ]
    image = models.ImageField(upload_to='backgrounds/')
    position = models.CharField(max_length=10, choices=POSITION_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.position} - {self.image.name}"

class UploadedDocument(models.Model):
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name