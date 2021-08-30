from exchange.api.permissions import IsOwnerProfile
from exchange.api.serializers import OrderSerializer
from exchange.models import Order
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    Order ViewSet.

    Actions
    - Create
    - Retrieve
    - List
    - Delete

    * Each action can only be performed by authenticated users.
    * Users can only access their own data.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerProfile]

    def get_queryset(self):
        """
        Override 'get_queryset()' method of GenericAPIView class.
        Retrieve 2 lists of 'ProfileStatus' instances.
        - Retrieve a list with all 'ProfileStatus' instances if request has no parameters.
        - Retrieve a list with all 'ProfileStatus' instances that correspond to the user passed as parameter in the request.
        """

        queryset = Order.objects.filter(profile=self.request.user.profile, status=True)
        kwarg_pk = self.kwargs.get('pk', None)
        if kwarg_pk is not None:
            queryset = queryset.filter(pk=kwarg_pk)
        return queryset

    def perform_create(self, serializer):
        """
        Override 'perform_create()' method of CreateModelMixin class.
        Set current session user's 'Profile' as 'user_profile' of the 'ProfileStatus' instance.
        * Method called when creating a new instance after receiving a POST request.
        """

        user_profile = self.request.user.profile
        serializer.save(profile=user_profile)
