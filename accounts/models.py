from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
# from django.contrib.gis.db import models as gismodels
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self,first_name,last_name,username,email,password=None):
        if not email:
            raise ValueError("User must have email adress")
        if not username:
            raise ValueError("User must have username adress")
        user = self.model(
            email = self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,

                    )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,first_name,last_name,username,email,password=None):
        user=self.create_user(
            email = self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        
        user.is_admin = True
        user.is_staff=True
        user.is_active=True
        user.is_superadmin = True

        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    VENDOR=1
    CUSTOMER = 2
    ROLE_CHOICE=(
        (VENDOR,'Vendor'),
        (CUSTOMER,'Customer')
    )
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    username=models.CharField(max_length=50,unique=True)
    email=models.EmailField(max_length=100,unique=True)
    phone_number=models.CharField(max_length=12, blank=True)
    role=models.PositiveSmallIntegerField(choices=ROLE_CHOICE,blank=True,null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']
    objects  = UserManager()

    def __str__(self):
        return self.email
    
    def has_perm(self,perm,obj=None):
        return self.is_admin
    
    def has_module_perms(self,app_label):
        return True


    # required fields
    date_joined=models.DateTimeField(auto_now_add=True)
    last_login=models.DateTimeField(auto_now_add=True)
    created_date=models.DateTimeField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now_add=True)
    is_admin= models.BooleanField(default=False)
    is_staff= models.BooleanField(default=False)
    is_active= models.BooleanField(default=False)
    is_superadmin= models.BooleanField(default=False)



class UserProfile(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='users/profile_pictures', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='users/cover_photos', blank=True, null=True)
    address_line_1 = models.CharField(max_length=50, blank=True, null=True)
    address_line_1 = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=15, blank=True, null=True)
    state = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    # location = gismodels.PointField(blank=True, null=True, srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


# @receiver(post_save,sender=User)
# def post_save_create_profile_receiver(sender,instance,created,**kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
#         print('user profile is created')
#     else:
#         print('user is updaated')
#         try:
#             profile = UserProfile.objects.get(user=instance)
#         except:
#             # create user profile if not exists
#              UserProfile.objects.create(user=instance)
#              print('user profile was not exists so created new one')
     
# @receiver(pre_save,sender=User)
# def pre_save_create_profile_receiver(sender,instance,**kwargs):

#     print(instance.username,"pre saved called")