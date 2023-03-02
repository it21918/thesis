from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from base.emailBackEnd import EmailBackEnd
from django.urls import reverse
from base.models import *
from django.views.decorators.csrf import csrf_protect
import logging
import os, io
import glob
from shutil import copy
from io import BytesIO, StringIO
from .forms import FilePreviewForm
from base64 import b64encode 
from PIL import Image as PIL_Image
import cv2
import base64
from django.contrib import messages
import numpy as np
from base.predict import predict
from django.core.files.base import ContentFile
from base.models import Image
from base.evaluate import eval
from base.train import training
from base.iou_score import *
import torch
from base.manageFolders import *
from django.utils.datastructures import MultiValueDictKeyError
import time
from pathlib import Path
from django.http import JsonResponse
from django.core import serializers
import json

def pivot_data(request):
    dataset = CustomUser.objects.all()
    data = serializers.serialize('json', dataset)
    return JsonResponse(data, safe=False)

def adminHome (request):
    user = request.user
    context = {}
    return render(request,"Admin/adminHome.html",{"context": context})

def train_model(request, experiment_id):
    return render(request, "train_model.html", {"experiment_id": experiment_id})
    
def train(request):
    # Log in to WandB
    wandb.login(key="3e1234cfe5ed344ab23cea32ea863b2d5c110f09")

    # Specify the name of your project
    project_name = "U-Net"

    # Initialize the WandB API
    api = wandb.Api()

    # Retrieve a list of all runs in your project
    runs = api.runs(project_name)

    trainImgCount = MultipleImage.objects.filter(purpose='train').count()
    trainImages = MultipleImage.objects.filter(purpose='train')  
    reportImgCount = MultipleImage.objects.filter(purpose='report').count()
    reportImages = MultipleImage.objects.filter(purpose='report')
    content = {
        'runCount': len(runs), 
        'runs': runs,
        'trainImgCount' : trainImgCount,
        'trainImages' : trainImages,
        'reportImages': reportImages,
        'reportImgCount': reportImgCount
    }

    return render(request, 'Admin/train.html', content)

def run_detail(request, run_id):
    # Initialize W&B API
    api = wandb.Api()

    # Get the run object using its ID
    run = api.run(f"dimitradan/U-Net/{run_id}")

    charts = run.history()
    data = run.summary._json_dict

    context = {
        'run': run,
        'charts': charts,
        'data': data
    } 
    return render(request, 'Admin/run_detail.html', context)


def trainSelected(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:   
        deleteFiles(os.path.join(settings.MEDIA_ROOT,'selected/image/train'))
        deleteFiles(os.path.join(settings.MEDIA_ROOT,'selected/mask/train')) 
        
        ids = request.POST.getlist('selected')
        trainImgs = MultipleImage.objects.filter(id__in=ids)

        for img in trainImgs:
            shutil.copyfile(os.path.join(settings.MEDIA_ROOT,img.images.name),(os.path.join(settings.MEDIA_ROOT+'/selected/image/train/',str(img.id)+'.jpg')))           
            shutil.copyfile(os.path.join(settings.MEDIA_ROOT,img.masks.name),(os.path.join(settings.MEDIA_ROOT+'/selected/mask/train/',str(img.id)+"_Segmentation.png")))                

        training()

        deleteFiles(os.path.join(settings.MEDIA_ROOT,'selected/image/train'))
        deleteFiles(os.path.join(settings.MEDIA_ROOT,'selected/mask/train')) 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
def imageToStr(img):
    with io.BytesIO() as buf:
        img.save(buf, 'jpeg')
        image_bytes = buf.getvalue()
    encoded = b64encode(image_bytes).decode()
    mime = 'image/jpeg;'
    img =  "data:%sbase64,%s" % (mime, encoded)
    return img

import wandb
def train_results(request): 

    pwd = os.path.dirname(__file__)
    # Open and read the log file
    with open('logs.txt', 'r') as file:
        logs = file.read() 
        logs=logs.replace("'",'"') 
        # Split the concatenated string into individual log entries
        log_entries = [entry.strip() for entry in logs.split('}') if entry.strip()]
        # Create a list to store the parsed log objects
        logs = []

        # Parse each log entry as a JSON object and append it to the logs list
        for entry in log_entries:
            log = json.loads(entry + '}')
            logs.append(log) 
        data = logs        

    # Extract relevant data for charts and tables
    train_loss_data = [{'x': d['step'], 'y': d['train_loss']} for d in data if 'train_loss' in d]
    validation_iou_data = [{'x': d['step'], 'y': d['validation_Iou']} for d in data if 'validation_Iou' in d]

    # Generate chart data as JSON
    train_loss_json = json.dumps(train_loss_data)
    validation_iou_json = json.dumps(validation_iou_data)

    images_dir = 'base/images/'
    image_pred_files=[]
    image_true_files=[]
    image_files=[]
    # Loop through each file in the directory
    for filename in os.listdir(images_dir):
        # Check if the file is an image
        if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
            # Open the image file
            img = PIL_Image.open(os.path.join(images_dir, filename))
            # Append the image to the list
            if 'pred' in filename:
                image_pred_files.append(imageToStr(img))
            if 'true' in filename:
                image_true_files.append(imageToStr(img))
            if 'images' in filename:
                image_files.append(imageToStr(img))
            img_list = zip(image_files, image_true_files, image_pred_files)
  


    # Render the template with chart and table data
    return render(request, 'Admin/trainResults.html', {'img_list': img_list ,'logs':logs,'train_loss_json': train_loss_json, 'validation_iou_json': validation_iou_json})

def evaluateModel(request):
    evaluationImgCount = MultipleImage.objects.filter(purpose='evaluate').count()
    evaluationImgs = MultipleImage.objects.filter(purpose='evaluate')

    context = {'evaluationImgCount': evaluationImgCount, 'evaluationImgs': evaluationImgs}
    return render(request,"Admin/evaluateModel.html",context)

def evaluation(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        count = int(request.POST.get('count'))
        evaluationImgs = MultipleImage.objects.filter(purpose='evaluate').order_by('?')[:count]
        evaluationImgs = evaluationImgs[:count]
        dir_img = "media/selected/image/evaluate/"
        dir_mask = "media/selected/mask/evaluate/"

        for img in evaluationImgs:
            Path(os.path.join(settings.MEDIA_ROOT,img.images.name)).rename(
            os.path.join(settings.MEDIA_ROOT+'/selected/',img.images.name))            
            Path(os.path.join(settings.MEDIA_ROOT,img.masks.name)).rename(
            os.path.join(settings.MEDIA_ROOT+'/selected/',img.masks.name))

        evalu, progress = eval(dir_img, dir_mask)

        y = []
        x = []
        i=1
        maxValScore = max(progress)
        minValScore = min(progress)
        for batch, files, mask in zip(progress, os.listdir(dir_img), os.listdir(dir_mask)):
            x.append(float("{:.1f}".format(batch)))
            y.append(i)
            i=i+1
            if maxValScore == batch:
                maxImg =  os.path.join('media/image/evaluate/',files)
                trueMaxMask = os.path.join('media/mask/evaluate/',mask)
                predictMaxImg = predict(PIL_Image.open(os.path.join(settings.MEDIA_ROOT+'/selected/image/evaluate/',files)))
            if minValScore == batch:
                minImg = os.path.join('media/image/evaluate/',files)
                trueMinMask = os.path.join('media/mask/evaluate/',mask)
                predictMinImg = predict(PIL_Image.open(os.path.join(settings.MEDIA_ROOT+'/selected/image/evaluate/',files)))

        for img in evaluationImgs:
            Path(os.path.join(settings.MEDIA_ROOT+'/selected/',img.images.name)).rename(
            os.path.join(settings.MEDIA_ROOT,img.images.name))            
            Path(os.path.join(settings.MEDIA_ROOT+'/selected/',img.masks.name)).rename(
            os.path.join(settings.MEDIA_ROOT,img.masks.name))
        
        print(trueMaxMask)
        context = {
            'evaluationScore':evalu.item(),
            'progress' : progress,
            'x': x,
            'y': y,
            'maxImg':maxImg,
            'minImg':minImg,
            'trueMaxMask':trueMaxMask,
            'trueMinMask':trueMinMask,
            'predictMaxImg': imageToStr(predictMaxImg),
            'predictMinImg': imageToStr(predictMinImg),
        }

        return render(request,"Admin/evaluateModel.html", context)


def imageToStr(img):
    with io.BytesIO() as buf:
        img.save(buf, 'jpeg')
        image_bytes = buf.getvalue()
    encoded = b64encode(image_bytes).decode()
    mime = 'image/jpeg;'
    img =  "data:%sbase64,%s" % (mime, encoded)
    return img

def modifyDoctors (request):
    users = CustomUser.objects.all()

    content = {
        'users' : users,
    }

    return render(request,"Admin/modifyDoctors.html",content)

def modifyImages (request):
    images = MultipleImage.objects.all()

    content = {
        'trainCount' : MultipleImage.objects.filter(purpose='train').count(),
        'evaluateCount' : MultipleImage.objects.filter(purpose='evaluate').count(),
        'reportCount': MultipleImage.objects.filter(purpose='report').count(),
        'images' : images
    }
    return render(request,"Admin/modifyImages.html",content)
from django.conf import settings

def deleteImage(request,image_id):
    try:
        image=MultipleImage.objects.get(id=image_id)
        image.delete()
        os.remove(os.path.join(settings.MEDIA_ROOT, image.images.name))
        os.remove(os.path.join(settings.MEDIA_ROOT, image.masks.name))

        messages.success(request,"Successfully deleted image")
        return HttpResponseRedirect(reverse("modifyImages"))
    except:
        messages.error(request,"Failed to delete image")
        return HttpResponseRedirect(reverse("modifyImages"))

def editDoctor(request,doctor_id):
    doctor = CustomUser.objects.get(id=doctor_id)
    return render(request,"Admin/editDoctor.html",{"doctor":doctor,"id":doctor_id})

# def editDoctorSave(request,doctor_id):
#     doctor = CustomUser.objects.get(id=doctor_id)
#     return render(request,"Admin/editDoctor.html",{"doctor":doctor,"id":doctor_id})

def editDoctorSave(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user_id=request.POST.get("user_id")
        password=request.POST.get("password")
        username=request.POST.get("username")
        email = request.POST.get("email")

        try:
            user=CustomUser.objects.get(id=user_id)
            user.username = username
            user.email = email
            user.password = password
            user.save()

            messages.success(request,"Successfully Edited user")
            return HttpResponseRedirect(reverse("editDoctor",kwargs={"doctor_id":user_id}))
        except:
            messages.error(request,"Failed to Edit user" )
            return HttpResponseRedirect(reverse("editDoctor",kwargs={"doctor_id":user_id}))

def deleteDoctor(request,doctor_id):
    try:
        user=CustomUser.objects.get(id=doctor_id)
        user.delete()
                
        messages.success(request,"Successfully deleted doctor")
        return HttpResponseRedirect(reverse("modifyDoctors"))
    except:
        messages.error(request,"Failed to delete doctor")
        return HttpResponseRedirect(reverse("modifyDoctors"))



def addImage(request): 
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        purpose = request.POST.get("purpose")
        imageFiles = request.FILES.getlist('imageFiles')
        maskFiles = request.FILES.getlist('maskFiles')

        if len(imageFiles) != len(maskFiles):
            messages.error(request,"Failed to Add images.List index out of range")
            return HttpResponseRedirect(reverse("modifyImages"))
        try:
            for (image, mask) in zip(imageFiles, maskFiles):
                MultipleImage.objects.create(images=image, masks=mask, purpose=purpose, postedBy=request.user)
            
            messages.success(request,"Successfully Added images")
            return HttpResponseRedirect(reverse("modifyImages"))
        except Exception as e:
            messages.error(request,e)
            return HttpResponseRedirect(reverse("modifyImages"))




