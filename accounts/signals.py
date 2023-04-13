from django.db.models.signals import post_save,pre_save
from .models import User,UserProfile
from django.dispatch import receiver



@receiver(post_save,sender=User)
def post_save_create_profile_receiver(sender,instance,created,**kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        print('user profile is created')
    else:
        print('user is updaated')
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # create user profile if not exists
             UserProfile.objects.create(user=instance)
             print('user profile was not exists so created new one')
     
# @receiver(pre_save,sender=User)
# def pre_save_create_profile_receiver(sender,instance,**kwargs):

#     print(instance.username,"pre saved called")