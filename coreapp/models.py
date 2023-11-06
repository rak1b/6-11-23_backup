from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin,Group
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from coreapp import constants
from coreapp.manager import MyUserManager
from .base import BaseModel
from utility.utils import slug_utils

from django.core.exceptions import ValidationError
import os
from PIL import Image
from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from django.core.files import File
from io import BytesIO
# Create your models here.

class Country(BaseModel):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    phone_code = models.CharField(_("Phone code"), max_length=50)
    flag = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=200)
    groups = models.ManyToManyField(Group)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ('-created_at',)
    def __str__(self):
        return self.name
    
class BillingInfo(BaseModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255,blank=True,null=True)
    company_name = models.CharField(max_length=255,blank=True,null=True)
    country = models.CharField(max_length=255)
    division = models.CharField(max_length=255,blank=True,null=True)
    district = models.CharField(max_length=255,blank=True,null=True)
    street_address = models.CharField(max_length=255)
    town_city = models.CharField(max_length=255,blank=True,null=True)
    redex_division = models.ForeignKey("utility.RedexDivision", on_delete=models.SET_NULL, blank=True, null=True)
    redex_district = models.ForeignKey("utility.RedexDistrict", on_delete=models.SET_NULL, blank=True, null=True)
    redex_area = models.ForeignKey("utility.RedexArea", on_delete=models.SET_NULL, blank=True, null=True)
    state_county = models.CharField(max_length=255,blank=True,null=True)
    postcode_zip = models.CharField(max_length=20,blank=True,null=True)
    mobile = models.CharField(max_length=20)
    email = models.EmailField()
    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    email = models.EmailField(unique=True)
    mobile = models.CharField( max_length=20, blank=True, null=True)
    slug = models.SlugField(max_length=250, null=True, blank=True)

    # image = models.ForeignKey('coreapp.Document', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to="user/profile",default="default/user_placeholder.jpg",  null=True, blank=True)
    gender = models.SmallIntegerField(
        choices=constants.GenderChoices.choices,
        blank=True, null=True
    )
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, blank=True, null=True)
    billing_info = models.ForeignKey(BillingInfo, on_delete=models.SET_NULL, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    joining_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    blood_group = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=250,null=True,blank=True)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_customer = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_outlet_user = models.BooleanField(default=False)
    outlet = models.ForeignKey("sales.Outlet", on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    objects = MyUserManager()
    class Meta:
        ordering = ('-created_at',)
    def __str__(self):
        return self.email

    @property
    def name(self):
        full_name = self.get_full_name()
        return full_name
    @property
    def image_url(self):
        from django.conf import settings
        base_url = settings.MEDIA_HOST
        url = base_url + self.image.url if self.image else f"{settings.USER_PLACEHOLDER_IMAGE}"
        return url    
    @property
    def get_image_url(self):
        from django.conf import settings
        base_url = settings.MEDIA_HOST
        url = base_url + self.image.url if self.image else f"{settings.USER_PLACEHOLDER_IMAGE}"
        return url

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name
    
  
            
    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.slug:
            self.slug = slug_utils.generate_unique_slug(self.name, self)

        return super(User, self).save(*args, **kwargs)


class UserConfirmation(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    confirmation_code = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=100)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.confirmation_code} : {self.is_used}"


class LoginHistory(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=100)
    user_agent = models.CharField(max_length=500)
    is_success = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.ip_address} - {self.user_agent} - {self.is_success}"


class Document(BaseModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,blank=True,null=True)
    document = models.FileField(upload_to='documents/%Y/%m/%d/')
    resize_document =  models.FileField(blank=True,upload_to='documents/resized/%Y/%m/%d/')
    doc_type = models.SmallIntegerField(choices=constants.DocumentChoices.choices)
    order = models.SmallIntegerField(default=0)
    height = models.IntegerField(default=300)
    width = models.IntegerField(default=300)

    def __str__(self):
        return f"{self.owner} - {self.document.name}"
    
    def save(self, *args, **kwargs):
        if self.document and self.doc_type == 0:

            from utility.utils.resize_utils import resize_image
            resized_image = resize_image(self.document, self.height, self.width)
            if resized_image:
                self.resize_document = resized_image

        super().save(*args, **kwargs)

    @cached_property
    def get_url(self):
        try:
            if self.document.url is None or self.document.url == "":
                return f"{settings.MEDIA_HOST}/media/default/lazy_placeholder.png"
            return f"{settings.MEDIA_HOST}{self.document.url}"
        except:
            return f"{settings.MEDIA_HOST}/media/default/lazy_placeholder.png"
        
    @cached_property
    def get_resized_url(self):
        return f"{settings.MEDIA_HOST}{self.resize_document.url}" if self.resize_document else self.get_url

