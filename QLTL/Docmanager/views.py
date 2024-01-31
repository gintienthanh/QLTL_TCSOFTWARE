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
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    
    
    
class PortfolioUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    

    
    
    
class DocumentList(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    
class DocumentUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class FolderList(generics.ListCreateAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    
    
    
class FolderUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class BoxCaseList(generics.ListCreateAPIView):
    queryset = BoxCase.objects.all()
    serializer_class = BoxcaseSerializer

class BoxCaseUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoxCase.objects.all()
    serializer_class = BoxcaseSerializer
    
class ShelfList(generics.ListCreateAPIView):
    queryset = Shelf.objects.all()
    serializer_class = ShelfSerializer

class ShelfUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shelf.objects.all()
    serializer_class = ShelfSerializer
    
    
class WarehouseList(generics.ListCreateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    
class WarehouseUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    
    
    
class WatchList(generics.ListCreateAPIView):
    queryset = Watchlist.objects.all()
    serializer_class = WatchListSerializer
                                                                                            
class WatchlistUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoxCase.objects.all()
    serializer_class = WarehouseSerializer
    