from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.text import slugify
from vendor.forms import VendorForm
from.models import User, UserProfile
from accounts.forms import UserForm
from django.contrib import  messages,auth
from .utils import detectUser
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied

#### restrict vendor from accessing  customer page

def check_role_vendor(user):
    if user.role ==1:
        return True
    else:
        raise PermissionDenied
    
#### restrict customer  from accessing  vendor page

def check_role_customer(user):
    if user.role ==2:
        return True
    else:
        raise PermissionDenied


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request,"You are already logged in")
        return redirect('dashboard')
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
    if request.user.is_authenticated:
        messages.warning(request,"You are already logged in")
        return redirect('dashboard')
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


def login(request):
    if request.user.is_authenticated:
        messages.warning(request,"You are already logged in")
        return redirect('myaccountdc')
    if request.method=="POST":
        email = request.POST['email']
        password = request.POST['password']
        user= auth.authenticate(email=email,password=password)
        if user is not None:
            auth.login(request,user)
            messages.success(request,'You are now logged in')
            return redirect('myaccount')
        else:
            messages.success(request,'You are now logged in')
            return redirect('login')
    return render(request,'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request,'You are logged out')
    return redirect('login')

def myaccount(request):
    user = request.user
    redirectUrl=detectUser(user)
    return redirect(redirectUrl)

@login_required
@user_passes_test(check_role_customer)
def custDashboard(request):
    return render(request,'accounts/customer_dashboard.html')

@login_required
@user_passes_test(check_role_vendor)
def VendorDashboard(request):
    return render(request,'accounts/vendor_dashboard.html')