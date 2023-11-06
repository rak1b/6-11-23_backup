from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentType(models.IntegerChoices):
    COD = 0, _("Cash On Delivery")
    CARD = 1, _("Card")
    BANK = 2, _("Bank")
    BKASH = 3, _("Bkash")
    SSLECOMMERZ = 4, _("SSLCOMMERZ")

class deliveryChargeChoices(models.IntegerChoices):
    INSIDE_DHAKA = 0, _("Inside Dhaka : 80/-")
    OUTSIDE_DHAKA = 1, _("Outside Dhaka : 150/-")
    CUSTOM = 2, _("Custom")
class CheckoutStatus(models.IntegerChoices):
    PENDING  = 0, _("Pending")
    SUCCESS = 1, _("Success")
    FAILED = 2, _("Failed")
