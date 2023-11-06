from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"outlet-product", views.OutletProductAPI, basename="outlet-product")
router.register(r"outlet-product-return", views.OutletProductReturnAPI, basename="outlet-product-return")

urlpatterns = [
    # path("<int:user>/product/<int:id>/", views.ProductGetApi.as_view()),
]
urlpatterns += router.urls
