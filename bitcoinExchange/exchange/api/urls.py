from django.urls import include, path
from exchange.api.views import LatestOrdersListAPIView, OrderViewSet, ProfileAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('orders/latest/', LatestOrdersListAPIView.as_view(), name='latest-orders'),
    path('', include(router.urls)),
]
