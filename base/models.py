from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from datetime import datetime

# class Image(models.Model):
#     name = models.CharField(max_length=50)
#     img = models.ImageField(upload_to='images/')

class CustomUser(AbstractUser):
    user_type_data = ((1, "Admin"), (2, "Doctor"), (3, "Patient"))
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)
    birthday = models.CharField(max_length=20)

def upload_path_img(self, filename):
    return f'image/{self.purpose}/{filename}'

def upload_path_mask(self, filename):
    return f'mask/{self.purpose}/{filename}'

class MultipleImage(models.Model):
    id = models.AutoField(primary_key=True)
    images = models.FileField(upload_to=upload_path_img, blank=True)
    masks = models.FileField(upload_to=upload_path_mask, blank=True)
    purpose = models.CharField(max_length=20)
    postedBy = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.now())

class Image(models.Model):
    id = models.AutoField(primary_key=True)
    purpose = models.CharField(max_length=20)
    image = models.CharField(max_length=10000)
    mask = models.CharField(max_length=10000)
    score = models.FloatField(null=True)

class Patient(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE) 
    image = models.ManyToManyField(Image)
    treatment = models.CharField(max_length=300)
    diagnosis = models.CharField(max_length=50)

class Doctor(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    specialisation = models.CharField(max_length=50, null=True )
    experience = models.CharField(max_length=50, null=True)
    patient = models.ManyToManyField(Patient)