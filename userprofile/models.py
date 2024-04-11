from django.db import models
from django.contrib.auth.models import User
# from store.models import Gender
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Q






class State(models.Model):
    state = models.CharField(max_length=20, null=True,blank=True)

    class Meta:
        ordering = ['state']
    
    def __str__(self): 
        return self.state
     
     
class Userprofile(models.Model):
    company_image = models.ImageField(null=True, blank=True, upload_to='uploads/profile_pic')
    user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE)
    company_whatsapp_number = PhoneNumberField(null=True, blank=True, verbose_name='WhatsApp')
    # gender = models.ForeignKey(Gender,related_name = "gender",on_delete=models.SET_NULL)
    company_address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Address')
    website = models.CharField(max_length=225, null=True, blank=True)
    about = models.TextField(blank=True, null=True)
    state = models.ForeignKey(State, max_length=20, null=True, blank=True, on_delete=models.SET_NULL)
    lga = models.CharField(max_length=20, null=True, blank=True)
    is_vendor = models.BooleanField(default=False)


    def __str__(self):
        return self.user.username
      
vendors = Userprofile.objects.filter(is_vendor=True)
non_vendors = Userprofile.objects.filter(~Q(is_vendor=True))







  