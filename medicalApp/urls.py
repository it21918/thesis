"""medicalApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from base import views, doctorViews, adminViews
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('data', adminViews.pivot_data, name='pivot_data'),
    path('', views.showLoginPage, name="showLoginPage"),
    path('doLogin', views.doLogin, name="doLogin"),
    path('logout', views.logout, name="logout"),
    path('sign_up', views.showSignUpPage, name="signUp"),
    path('doSignUp', views.doSignUp, name='doSignUp'),
    path('doctorHome', doctorViews.doctorHome, name="doctorHome"),
    path('adminHome', adminViews.adminHome, name="adminHome"),
    path('modifyImages', adminViews.modifyImages, name="modifyImages"),
    path('evaluateModel', adminViews.evaluateModel, name="evaluateModel"),
    path('evaluation', adminViews.evaluation, name="evaluation"),
    path('modifyDoctors', adminViews.modifyDoctors, name="modifyDoctors"),
    path('add_image', adminViews.addImage, name="add_image"),
    path('Segmentation', doctorViews.segmentation, name="segmentation"),    
    path('Patients', doctorViews.patients, name="patients"),    
    path('delete_image/<str:image_id>', adminViews.deleteImage,name="delete_image"),
    path('delete_doctor/<str:doctor_id>', adminViews.deleteDoctor,name="delete_doctor"),
    path('editDoctor/<str:doctor_id>', adminViews.editDoctor,name="editDoctor"),
    path('edit_doctor_save', adminViews.editDoctorSave,name="edit_doctor_save"),
    path('trainModel', adminViews.train, name='train'),
    path('train_selected', adminViews.trainSelected, name='train_selected'),
    path('train_results', adminViews.train_results, name='train_results'),
    path('run_detail/<str:run_id>/', adminViews.run_detail, name='run_detail'),

]
 
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
