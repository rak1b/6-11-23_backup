from django.db import models
from coreapp.base import BaseModel
from . import constants
from utility.utils import model_utils
from inventory.constants import MainCategoryChoices
from django.conf import settings
# Create your models here.
class Offer(BaseModel):
  offer_id = models.CharField(max_length=20,blank=True,null=True)
  name = models.CharField(max_length=200)
  category = models.ManyToManyField("inventory.Category",blank=True)
  product = models.ManyToManyField("inventory.Products",blank=True)
  banner = models.ForeignKey("coreapp.Document",on_delete=models.SET_NULL,null=True,blank=True)
  description = models.TextField(blank=True,null=True)
  discount_type = models.SmallIntegerField(choices=constants.OfferType.choices,default=constants.OfferType.PERCENTAGE)
  discount_value = models.IntegerField(default=0.00)
  start_date = models.DateTimeField()
  expiry_date = models.DateTimeField()
  is_active = models.BooleanField(default=True)

  @property
  def discount_type_name(self):
    return "%" if self.discount_type == constants.OfferType.PERCENTAGE else "৳"
  
  def get_banner_url(self):
    placeholder = f"{settings.PLACEHOLDER_IMAGE}"
    return self.banner.get_url if self.banner else placeholder

  def __str__(self) -> str:
    return self.name
  
  def get_all_products(self):
    from inventory.models import Products,Category
    # products = Products.objects.filter(category__in=self.category.all())
    # return self.product.all().union(products)
    return self.product.all()

  def save(self, *args, **kwargs):
    if not self.id :
      self.offer_id = model_utils.get_code(Offer)
    super(Offer, self).save(*args, **kwargs)
    


class Wishlist(BaseModel):
    user = models.ForeignKey("coreapp.User", on_delete=models.CASCADE,
                                    related_name="user_wishlist")
    product = models.ForeignKey("inventory.Products", on_delete=models.CASCADE,
                                    related_name="product_wishlist")
    variant = models.ForeignKey("inventory.Variant", on_delete=models.CASCADE,blank=True,null=True)
    is_active = models.BooleanField(default=True)
   
    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.user.get_full_name + " - " + self.product.name
    



class Review(BaseModel):
  product = models.ForeignKey("inventory.Products", on_delete=models.CASCADE,blank=True,null=True)
  star = models.SmallIntegerField(default=0) 
  reviewed_by = models.ForeignKey("coreapp.User", on_delete=models.CASCADE)
  photos = models.ManyToManyField('coreapp.Document', related_name='review_photos',blank=True)
  descriptions = models.TextField()
  is_active = models.BooleanField(default=True)
  first_name = models.CharField(max_length=255, blank=True)
  last_name = models.CharField(max_length=255, blank=True)
          
  def __str__(self):
    return self.reviewed_by.first_name + "'review"
  
  def save(self, *args, **kwargs):
    if not self.id :
      from utility.utils import notification_utils
      notification_utils.update_dashboard_notification("review",1,True)
    super().save(*args, **kwargs)
  
class Banner(BaseModel):
  main_category = models.SmallIntegerField(choices=MainCategoryChoices.choices,default=0)
  name = models.CharField(max_length=200)
  image = models.ForeignKey("coreapp.Document",on_delete=models.CASCADE)
  description = models.TextField()
  is_active = models.BooleanField(default=True)
  order = models.PositiveSmallIntegerField()
  def __str__(self):
    return self.name
  
  class Meta:
    ordering = ('order',)