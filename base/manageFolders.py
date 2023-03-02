
import logging
import os, shutil
import cv2
import base64
import numpy as np

def readb64(encoded_image):
    header, data = encoded_image.split(',', 1)
    image_data = base64.b64decode(data)
    np_array = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_UNCHANGED)
    return image 

def deleteFiles(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def insertToFolder(folderImage, folderMask, objs):
    for obj in objs :
        _, _, imageFiles = next(os.walk(folderImage))
        _, _, maskFiles = next(os.walk(folderMask))
        cv2.imwrite(os.path.join(folderImage+'ISIC_' + str(len(imageFiles)) + '.jpg'), readb64(obj.image))
        cv2.imwrite(os.path.join(folderMask +'ISIC_' + str(len(maskFiles)) + '_Segmentation.png'), readb64(obj.mask)) 

def insertFromFolderTodatabase(dir_img, dir_mask, purpose):
    # dir_img = "base/images_mask/images/"
    # dir_mask = "base/images_mask/masks/"

    for idx, filename in enumerate(os.listdir(dir_img)):
        id=0
        for mask in (os.listdir(dir_mask)):
            if id == idx:
                filename = f'{dir_img}{filename}'
                mask = f'{dir_mask}{mask}' 
                imga = Image(image=img(filename),purpose=purpose, mask=img(mask))
                imga.save()
            id = id + 1  

def insertFromFolderToArray(dir_img, dir_mask, purpose):
    # dir_img = "base/images_mask/images/"
    # dir_mask = "base/images_mask/masks/"
    imga = []
    for idx, filename in enumerate(os.listdir(dir_img)):
        id=0
        for mask in (os.listdir(dir_mask)):
            if id == idx:
                filename = f'{dir_img}{filename}'
                mask = f'{dir_mask}{mask}' 
                imga.append(Image(image=img(filename),purpose=purpose, mask=img(mask)))
            id = id + 1  
    return imga