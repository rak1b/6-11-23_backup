from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"outlet", views.OutletAPI, basename="outlets")
router.register(r"chalan", views.ChalanAPI, basename="chalan")


urlpatterns = [
    # path("<int:user>/product/<int:id>/", views.ProductGetApi.as_view()),
]
urlpatterns += router.urls
