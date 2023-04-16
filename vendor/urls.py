from django.urls import include, path
from . import views
from accounts import views as accountviews

urlpatterns = [
    path('',accountviews.VendorDashboard,name='vendor'),
    path('profile/',views.vprofile,name='vprofile'),
    

]
