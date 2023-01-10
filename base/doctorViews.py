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
from PIL import Image, ImageDraw, ImageFilter
import cv2
import base64
from django.contrib import messages
import numpy as np
from base.predict import predict
from django.core.files.base import ContentFile
from base.models import MRI


def doctorHome (request):
    user = request.user
    patientcount = Patient.objects.filter(user_id=user.doctor.id).count()
    context = {
    'patientcount': patientcount,
    'doctor': Doctor.objects.get(id=user.id), 
    }
    return render(request,"doctorHome.html",{"context": context})

def imageToStr(img):
    with io.BytesIO() as buf:
        img.save(buf, 'jpeg')
        image_bytes = buf.getvalue()
    encoded = b64encode(image_bytes).decode()
    mime = 'image/jpeg;'
    img =  "data:%sbase64,%s" % (mime, encoded)
    return img

def segmentation(request):
    if 'submit' in request.POST:
        try :
            file = request.FILES['fileInput']        
            data = file.read()
            encoded = b64encode(data).decode()
            mime = 'image/jpeg;'
            imagep = Image.open(file)
            mask = predict(imagep)
            image = "data:%sbase64,%s" % (mime, encoded)
            imgAndMask = Image.composite(imagep.convert('RGB'), mask.convert('RGB'), mask)

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
        try :
            createMask(image, all_points_x, all_points_y)

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

def createMask(img, x_points, y_points) :
    img = readb64(img)
    w, h, c = img.shape

    MASK_HEIGHT = h
    MASK_WIDTH = w
    all_points = []
    for i, x in enumerate(x_points.split(",")):
        all_points.append([int(x), int(y_points.split(',')[i])]) 

    arr = np.array(all_points)
    mask = np.zeros((MASK_WIDTH, MASK_HEIGHT)) 
    mask = cv2.fillPoly(mask, [arr] , color=(255))

    _, _, files = next(os.walk("base/images_mask/masks"))
    file_count = len(files)
    cv2.imwrite(os.path.join('base/images_mask/masks/ISIC_' + str(file_count) + '_Segmentation.png'), mask)
    cv2.imwrite(os.path.join('base/images_mask/images/ISIC_' + str(file_count) + '.jpg'), img)

    # MRI(image=numpyToImg(img), mask=numpyToImg(mask), name='report').save()
    # MRI.mask.save('output.jpg', numpyToImg(img), save=True)
    # MRI.image.save('input.jpg', numpyToImg(mask), save=True)
     

def numpyToImg(img): 
    ret, buf = cv2.imencode('.jpg', img)
    content = ContentFile(buf.tobytes())
    return content


    
 
 



