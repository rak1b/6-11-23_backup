from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"page", views.PageAdminAPI)
router.register(r"social-media", views.SocialMediaAPI)
router.register(r"testimonial", views.TestimonialAdminAPI)
router.register(r"slider", views.SliderAdminAPI)
router.register(r"team-member", views.TeamMemberAPI)
router.register(r"contact-us", views.ContactUsAPI)
router.register(r"display-center", views.DisplayCenterAPI)
router.register(r"dashboard-notifications", views.DashboardNotificationAPI)
router.register(r"custom-delivery-charge", views.CustomDeliveryChargeAPI)
router.register(r"redex-address", views.RedexAddressAPI)

urlpatterns = [
    path("global-settings/", views.GlobalSettingsAPI.as_view())
]
urlpatterns += router.urls
