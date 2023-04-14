from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.text import slugify
from vendor.forms import VendorForm
from.models import User, UserProfile
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


def registerVendor(request):
    if request.method=='POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST,request.FILES)

        if form.is_valid() and v_form.is_valid():
            # user = form.save(commit=False)
            # user.role = User.VENDOR
            # user.save()
            ######## or ######
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(request,"your account registered successfully. Please wait for approval.")
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()
    context = {
        'form':form,
        'v_form': v_form,
    }
    return render(request,'accounts/registerVendor.html',context)