from django.shortcuts import render
from django.shortcuts import render
from .model_serializers import*
from .models import*
from rest_framework import authentication, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
# Create your views here.


class PortfolioList(generics.ListCreateAPIView):
    queryset = Portfolios.objects.all()
    serializer_class = PortfolioSerializer
    
class PortfolioUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Portfolios.objects.all()
    serializer_class = PortfolioSerializer
    
class DocumentList(generics.ListCreateAPIView):
    queryset = Documents.objects.all()
    serializer_class = DocumentSerializer
    
class DocumentUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Documents.objects.all()
    serializer_class = DocumentSerializer
    
class FolderList(generics.ListCreateAPIView):
    queryset = Folders.objects.all()
    serializer_class = FolderSerializer
    
class FolderUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Folders.objects.all()
    serializer_class = FolderSerializer

class BoxCaseList(generics.ListCreateAPIView):
    queryset = BoxCase.objects.all()
    serializer_class = BoxcaseSerializer
    
class ShelfList(generics.ListCreateAPIView):
    queryset = Shelf.objects.all()
    serializer_class = ShelfSerializer
    
class WarehouseList(generics.ListCreateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    
class WatchList(generics.ListCreateAPIView):
    queryset = Watchlist.objects.all()
    serializer_class = WatchListSerializer
    
