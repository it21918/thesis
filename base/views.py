from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from base.emailBackEnd import EmailBackEnd
from django.urls import reverse
from base.models import CustomUser

def showLoginPage(request):
    return render(request, "loginPage.html")

def showSignUpPage(request):
    return render(request, "signUpPage.html")

def doSignUp(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        username = request.POST.get("username")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")
        password= request.POST.get("password")
        try:
            user=CustomUser.objects.create_user(
                username = username,
                lastname= lastname,
                email=email,
                password=password,
                is_staff = False,
                is_active = True,
                is_superuser = False
            )
            user.save()
            messages.success(request,"Successfully Added user")
            return HttpResponseRedirect(reverse("signUp"))
        except:
            messages.error(request,"Failed to Add user")
            return HttpResponseRedirect(reverse("signUp"))


def doLogin(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user = EmailBackEnd.authenticate(request, username=request.POST.get("email"),
                                         password=request.POST.get("password"))
        if user != None:
            login(request, user)
            if user.user_type == "2":
                return HttpResponseRedirect('/doctorHome')
            # elif user.user_type == "2":
            #     return HttpResponseRedirect("/")
            # else:
            #     return HttpResponseRedirect("/")
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect("/")


def logout(request):
    logout(request)
    return HttpResponseRedirect("/")
