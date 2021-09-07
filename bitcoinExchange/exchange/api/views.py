from django.shortcuts import get_object_or_404
from exchange.api.permissions import IsOwnerProfile
from exchange.api.serializers import LatestOrdersSerializer, OrderSerializer, ProfileSerializer
from exchange.models import Order, Profile
from rest_framework import mixins, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    Order ViewSet.

    :actions
    - list
    - create
    - retrieve
    - delete

    * Each action can only be performed by authenticated users.
    * Users can only access their own data.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerProfile]

    def get_queryset(self):
        """
        Two types of possible queryset:
        - A list with all user's order instances.
        - A specific user's order instance.
        """

        queryset = Order.objects.filter(profile=self.request.user.profile)
        kwarg_pk = self.kwargs.get('pk', None)
        if kwarg_pk is not None:
            queryset = queryset.filter(pk=kwarg_pk)
        return queryset

    def perform_create(self, serializer):
        user_profile = self.request.user.profile
        serializer.save(profile=user_profile)


class LatestOrdersListAPIView(ListAPIView):
    """
    Order ListAPIView.
    Retrieve a list of all active orders that have not been published by the current user.

    :actions
    - list

    * Only authenticated users can perform any action.
    """

    serializer_class = LatestOrdersSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(status=True).exclude(profile=self.request.user.profile)
        return queryset


class ProfileAPIView(APIView):
    """
    Profile APIView.
    Retrieve all profile details and wallet statistics of the current user.

    :actions
    - retrieve

    * Only authenticated users can perform any action.
    """

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.serializer_class(profile)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
