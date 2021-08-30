from django.urls import include, path
from exchange.api.views import OrderViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls))
]
