from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"offer", views.OfferAPI, basename="offer")
router.register(r"review", views.ReviewAPI, basename="review")
router.register(r"banner", views.BannerAPI, basename="banner")
urlpatterns = [
    # path("global-settings/", views.GlobalSettingsAPI.as_view())
]
urlpatterns += router.urls
