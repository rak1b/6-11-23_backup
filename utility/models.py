import uuid

from django.db import models
from django.utils.functional import cached_property

from coreapp.base import BaseModel
from utility import constants
from .utils import slug_utils

from django.core.exceptions import ValidationError
from utility.utils import notification_utils
from io import BytesIO
import base64
class SocialMedia(BaseModel):
    name = models.CharField(max_length=100)
    thumb = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE)
    url = models.CharField(max_length=100)
    def __str__(self):
        return self.name

    @cached_property
    def get_thumb_url(self):
        return self.thumb.get_url

class TeamMember(BaseModel):
    name = models.CharField(max_length=100)
    thumb = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE)
    designation = models.CharField(max_length=100)
    def __str__(self):
        return self.name

    @cached_property
    def get_thumb_url(self):
        return self.thumb.get_url

class Testimonial(BaseModel):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    comment = models.TextField()
    thumb = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE)
    def __str__(self):
        return self.name

    @cached_property
    def get_thumb_url(self):
        return self.thumb.get_url

class Contact(BaseModel):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    inquiry_type = models.SmallIntegerField(choices=constants.InquiryType.choices, default=constants.InquiryType.NORMAL)
    message = models.TextField(blank=True,null=True)
    document = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE,blank=True,null=True)
    contact_type = models.SmallIntegerField(choices=constants.ContactType.choices, default=constants.ContactType.CONTACT)
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            if self.contact_type == 0:
                notification_utils.update_dashboard_notification("contact_us",1,True)
            if self.contact_type == 1:
                notification_utils.update_dashboard_notification("work_us",1,True)
        super().save(*args, **kwargs)

class Subscription(BaseModel):
    email = models.CharField(max_length=100)
    def __str__(self):
        return self.email

class GlobalSettings(BaseModel):
    site_name = models.CharField(max_length=100)
    website_url = models.CharField(max_length=100)
    logo = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE, related_name="logo")
    qr_code = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE, related_name="qr_code",blank=True,null=True)
    qr_code2 = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE, related_name="qr_code2",blank=True,null=True)
    payment_method_images = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE,related_name="payment_method_image")
    about_us_image = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE,related_name="about_us_image")
    offer_banner = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE,related_name="offer_banner_image",blank=True,null=True)
    new_arrival_banner = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE,related_name="new_arrival_banner_image",blank=True,null=True)
    about_us_banner = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE,related_name="about_us_banner_image",blank=True,null=True)
    about_us_text = models.TextField()
    delivery_information = models.TextField()
    privacy_policy = models.TextField()
    terms_and_condition = models.TextField()
    search_terms = models.TextField()
    return_and_refund = models.TextField()
    brand_images = models.ManyToManyField("coreapp.Document",related_name="brand_images",blank=True)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=150)
    inside_dhaka = models.IntegerField(default=80)
    outside_dhaka = models.IntegerField(default=150)
    is_free_delivery = models.BooleanField(default=False)


    @cached_property
    def get_logo_url(self):
        return self.logo.get_url
    
    @cached_property
    def get_about_us_image_url(self):
        return self.about_us_image.get_url if self.about_us_image else self.get_default
    @cached_property
    def get_about_us_banner_url(self):
        return self.about_us_banner.get_url if self.about_us_banner else self.get_default
    @cached_property
    def get_offer_banner_url(self):
        return self.offer_banner.get_url if self.offer_banner else self.get_default
    
    @cached_property
    def get_about_banner_url(self):
        return self.about_us_banner.get_url if self.about_us_banner else self.get_default
    
    @cached_property
    def get_new_arrival_banner_url(self):
        return self.new_arrival_banner.get_url if self.new_arrival_banner else self.get_default

    @cached_property
    def get_payment_method_images_url(self):
        return self.payment_method_images.get_url if self.payment_method_images else ""

    @cached_property
    def get_qr_code_url(self):
        return self.qr_code.get_url if self.qr_code else ""
    @cached_property
    def get_qr_code_url2(self):
        return self.qr_code2.get_url if self.qr_code2 else ""
    @cached_property
    def get_video_url(self):
        return self.video.get_url if self.video else ""

    def __str__(self):
        return self.site_name
class Slider(BaseModel):
    title = models.CharField(max_length=100)
    desc = models.TextField(blank=True, null=True)
    image = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE, related_name="slider_image")
    is_active = models.BooleanField(default=0)
    order = models.PositiveSmallIntegerField(default=1)
    def __str__(self):
        return self.title

    @cached_property
    def get_image_url(self):
        return self.image.get_url if self.image else ""
    
    class Meta:
        ordering = ['order']

class Page(BaseModel):
    title = models.CharField(max_length=100)
    desc = models.TextField()
    slug = models.CharField(max_length=100, unique=True, db_index=True, editable=False)
    thumbnail = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE, related_name="page_thumbnail")
    slider = models.ManyToManyField("Slider",related_name="page_slider",blank=True)
    # video_url = models.CharField(max_length=100, null=True, blank=True)
    # blob_url = models.TextField(null=True, blank=True)
    video = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE, related_name="page_video",null=True, blank=True)
    page_type = models.SmallIntegerField(choices=constants.PageType.choices)
    show = models.SmallIntegerField(choices=constants.ShowType.choices,default=constants.ShowType.VIDEO)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @cached_property
    def get_thumbnail_url(self):
        return self.thumbnail.get_url    


    @property
    def get_video_url(self):
        return self.video.get_url if self.video else ""
    
    def get_sliders(self):
        return self.slider.all()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_utils.generate_unique_slug(self.title, self)
        # self.blob_url = self.video_to_blob_url(self.video.document.path) if self.video else ""
        super(Page, self).save(**kwargs)


class Payment(BaseModel):
    uid = models.UUIDField(default=uuid.uuid4, db_index=True, editable=False)
    amount = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    ip_address = models.CharField(max_length=100)
    status = models.SmallIntegerField(
        choices=constants.PaymentStatus.choices,
        default=constants.PaymentStatus.PENDING
    )
    payment_method = models.SmallIntegerField(choices=constants.PaymentMethod.choices)
    bill_uid = models.CharField(max_length=100, null=True, blank=True)
    bill_url = models.TextField()

    def __str__(self):
        return self.bill_uid


class Display_Center(BaseModel):
    thumb = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE, related_name="display_center_thumb",blank=True,null=True)
    name = models.CharField(max_length=100)
    # location = models.CharField(max_length=100)
    location_url = models.URLField()
    mobile = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=20, decimal_places=16,blank=True, null=True)    
    longitude = models.DecimalField(max_digits=20, decimal_places=16,blank=True,null=True)
    description = models.TextField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    @cached_property
    def get_thumb_url(self):
        return self.thumb.get_url if self.thumb else self.get_default



class DashboardNotification(BaseModel):
  user = models.ForeignKey("coreapp.User",on_delete=models.CASCADE)
  review = models.SmallIntegerField(default=0)
  invoice = models.SmallIntegerField(default=0)
  contact_us = models.SmallIntegerField(default=0)
  work_us = models.SmallIntegerField(default=0)
  notification = models.SmallIntegerField(default=0)
  def __str__(self) -> str:
    return f"Dashboard Notification for {self.user.email}"
  

from django.db import models

class District(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    division_id = models.CharField(max_length=10)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class PostCode(models.Model):
    upazila = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    postCode = models.CharField(max_length=10)

    def __str__(self):
        return self.name
class Division(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)
    bn_name = models.CharField(max_length=255)
    lat = models.CharField(max_length=20)
    long = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Upazilla(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    district_id = models.CharField(max_length=10)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class CustomDeliveryCharge(BaseModel):
    price = models.IntegerField(default=150)
    upazilla = models.ManyToManyField("Upazilla",related_name="upazilla")
    user = models.ForeignKey("coreapp.User",on_delete=models.CASCADE)

    def __str__(self):
        return __str__(self.price)



class RedexDivision(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)


    def __str__(self):
        return self.name
    
    def get_districts(self):
        return RedexDistrict.objects.filter(division=self)

class RedexDistrict(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    division = models.ForeignKey(RedexDivision, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_areas(self):
        return RedexArea.objects.filter(district=self)  

class RedexArea(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    district = models.ForeignKey(RedexDistrict, on_delete=models.CASCADE)
    division = models.ForeignKey(RedexDivision, on_delete=models.CASCADE)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2)
    inside_dhaka = models.BooleanField()
    def __str__(self):
        return f"{self.name} - {self.district.name} - {self.division.name} - {self.delivery_charge}"