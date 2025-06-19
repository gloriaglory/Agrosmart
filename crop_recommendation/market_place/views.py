from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import MarketplaceItem
from .serializers import MarketplaceItemSerializer

# Create your views here.
class MarketplaceItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows marketplace items to be viewed or edited.
    Supports GET, POST, PUT, PATCH, and DELETE methods.
    """
    queryset = MarketplaceItem.objects.all()
    serializer_class = MarketplaceItemSerializer

    def list(self, request):
        """Handle GET request to list all items"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Handle POST request to create a new item"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Handle PUT request to update an item"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """Handle PATCH request to partially update an item"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
