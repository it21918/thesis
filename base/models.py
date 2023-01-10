from django.contrib.auth.models import AbstractUser
from django.db import models

class Image(models.Model):
    name = models.CharField(max_length=50)
    img = models.ImageField(upload_to='images/')

class CustomUser(AbstractUser):
    user_type_data = ((1, "Admin"), (2, "Doctor"), (3, "Patient"))
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)
    birthday = models.CharField(max_length=20)
    profile_picture = models.ImageField(default='https://i.pinimg.com/236x/4d/a8/bb/4da8bb993057c69a85b9b6f2775c9df2.jpg')

class MRI(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField()
    mask = models.ImageField()
    name = models.CharField(max_length=20)

class Patient(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    MRI = models.ManyToManyField(MRI)
    treatment = models.CharField(max_length=300)
    diagnosis = models.CharField(max_length=50)

class Doctor(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    specialisation = models.CharField(max_length=50, null=True )
    experience = models.CharField(max_length=50, null=True)
    patient = models.ManyToManyField(Patient, null=True)