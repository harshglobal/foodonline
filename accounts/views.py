from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.text import slugify
from vendor.forms import VendorForm
from vendor.models import Vendor
from.models import User, UserProfile
from accounts.forms import UserForm
from django.contrib import  messages,auth
from .utils import detectUser,send_verification_email
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

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
            # send verification email
            mail_subject = 'Please Activate Your Account'
            email_template ='accounts/emails/account_verification_email.html'
            send_verification_email(request, user,mail_subject,email_template)
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
            # send verification email
            mail_subject = 'Please Activate Your Account'
            email_template ='accounts/emails/account_verification_email.html'
            send_verification_email(request, user,mail_subject,email_template)
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

@login_required(login_url='login')
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
    vendor = Vendor.objects.get(user=request.user)
    context = {
        'vendor' :vendor
    }
    return render(request,'accounts/vendor_dashboard.html',context)


def activate(request, uidb64, token):
    # Activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulation! Your account is activated.')
        return redirect('myaccount')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('myaccount')
    


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Reset Your Password'
            email_template ='accounts/emails/reset_password_email.html'
            send_verification_email(request, user,mail_subject,email_template)

            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
    return render(request, 'accounts/emails/forgot_password.html')







def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid  # this means pk
        messages.info(request,"please reset yout password")
        return redirect('reset_password')
    else:
        messages.error(request,"This link has been expired")
        return redirect('myaccount')



def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            # user.is_active = True
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    return render(request, 'accounts/emails/reset_password.html')