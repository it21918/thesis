from django import forms
from .models import *
 

class FilePreviewForm(forms.Form):
    image = forms.ImageField(help_text="Upload image: ", required=False)
