from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from.models import User
from accounts.forms import UserForm
from django.contrib import  messages
# Create your views here.

def registerUser(request):
    if request.method=='POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.CUSTOMER
            password = form.cleaned_data['password']
            user.set_password(password)
            user=form.save()
            messages.success(request,"Your account has been registered successfully ")
            return redirect ('registerUser')
        else:
           print('invalid form')
           print(form.errors)
    else:
        form = UserForm
    context = {
            'form':form
        }
    return render(request,'accounts/registerUser.html',context)