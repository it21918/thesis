from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from base.emailBackEnd import EmailBackEnd
from django.urls import reverse
from base.models import CustomUser, Doctor, Patient
from django.views.decorators.csrf import csrf_protect
import logging
import os, io
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
from base.models import *

def imageToStr(img):
    with io.BytesIO() as buf:
        img.save(buf, 'jpeg')
        image_bytes = buf.getvalue()
    encoded = b64encode(image_bytes).decode()
    mime = 'image/jpeg;'
    img =  "data:%sbase64,%s" % (mime, encoded)
    return img

def doctorHome (request):
    user = request.user
    patientcount = user.doctor.patient.all().count()
    context = {
    'patientcount': patientcount,
    # 'doctor': Doctor.objects.get(user_id=user.id), 
    }
    return render(request,"doctorHome.html",{"context": context})

# def img(img):
#     img = PIL_Image.open(img)
#     with io.BytesIO() as buf:
#         img.save(buf, 'jpeg')
#         image_bytes = buf.getvalue()
#     encoded = b64encode(image_bytes).decode()
#     mime = 'image/jpeg;'
#     img =  "data:%sbase64,%s" % (mime, encoded)

#     return str(img)

def segmentation(request):

    if 'submit' in request.POST:
        try :
            file = request.FILES['fileInput']        
            data = file.read()
            encoded = b64encode(data).decode()
            mime = 'image/jpeg;'
            imagep = PIL_Image.open(file)
            mask = predict(imagep)
            image = "data:%sbase64,%s" % (mime, encoded)
            imgAndMask = PIL_Image.composite(imagep.convert('RGB'), mask.convert('RGB'), mask)

            context = {
                "imageAndMask": imageToStr(imgAndMask), 
                "mask": imageToStr(mask),
                "image": image,  
            }

            return render(request, 'carouselimages.html', context)
        except :
            messages.error(request,"Failed to upload")
            return HttpResponseRedirect(reverse("segmentation"))

    if 'submitReport' in request.POST:
        all_points_x = request.POST.get('x')
        all_points_y = request.POST.get('y')
        image = request.POST.get('i')
        mask = request.POST.get('m')
        imgAndMask = request.POST.get('im')

        context = {
                "imageAndMask": imgAndMask, 
                "mask": mask,
                "image": image,  
        }
        
        createMask(request, image, all_points_x, all_points_y)
        try :

            messages.success(request, "Thank you for your feedback!")
            return render(request, 'carouselimages.html', context)
        except :
            messages.error(request,"Failed to send feedback...")
            return render(request, 'carouselimages.html', context)


    return render(request, 'uploadImagePage.html')

def readb64(encoded_image):
    header, data = encoded_image.split(',', 1)
    image_data = base64.b64decode(data)
    np_array = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_UNCHANGED)
    return image 

def createMask(request, image, x_points, y_points) :
    img = readb64(image)
    w, h, c = img.shape

    MASK_HEIGHT = h
    MASK_WIDTH = w
    all_points = []
    for i, x in enumerate(x_points.split(",")):
        all_points.append([int(x), int(y_points.split(',')[i])]) 

    arr = np.array(all_points)
    mask = np.zeros((MASK_WIDTH, MASK_HEIGHT)) 
    mask = cv2.fillPoly(mask, [arr] , color=(255)) 
    mask = arrayTo64Mask(mask)
    MultipleImage( 
        images=base64_file(image),
        purpose='report',  
        masks=base64_file(mask),
        postedBy=request.user
    ).save() 

def base64_file(data, name=None):
    _format, _img_str = data.split(';base64,')
    _name, ext = _format.split('/')
    if not name:
        name = _name.split(":")[-1]
    return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))

# def name(data):
#     _format, _img_str = data.split(';base64,')
#     _name, ext = _format.split('/')
#     name = _name.split(":")[-1]
#     return name

def arrayTo64Mask(img):
    pil_img = PIL_Image.fromarray(img)
    pil_img = pil_img.convert("L")
    buff = BytesIO()
    pil_img.save(buff, format="jpeg")
    encoded = base64.b64encode(buff.getvalue()).decode("utf-8")
    mime = 'image/jpeg;'
    img =  "data:%sbase64,%s" % (mime, encoded)
    return img

def patients(request):
    user = request.user
    patients = user.doctor.patient.all() 
    logging.warning(patients) 

    content = {
        "user" : user,
        "patients" : patients
        # "patientMoreInfo" : patientMoreInfo
    }

    return render(request, 'patients.html', content)



 