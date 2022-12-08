from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.

def log_user(request):
    if request.method == "POST":
        username = request.POST['loguser']
        password = request.POST['logpass']
        user = authenticate(username = username, password = password)     
        if user is not None:
            login(request, user)
            firstname = user.first_name
            return redirect('home')
        else:
            messages.error(request,"Erreur d'authentification ...")
            return redirect('login')
    return render(request, 'authentication/index.html')

def log_out(request):
    logout(request)
    messages.success(request, "Vous avez bien etait déconecté")
    return redirect('login')   

