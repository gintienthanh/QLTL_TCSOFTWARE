from django.shortcuts import render
from rest_framework import status,generics,serializers,permissions
from rest_framework.views import APIView, View
from rest_framework.response import Response
from django.http import HttpResponse,JsonResponse
from .model_serializers import BaseSerializers,BoxCaseSerializers,ShelfSerializers,FolderSerializers,PortfolioSerializers,DocumentSerializers,WarehouseSerializers,WatchlistSerializers
from .models import Base,BoxCase,Shelf,Document,Portfolio,Warehouse,Folder,Watchlist

# Create your views here.

class WarehouseView(generics.ListCreateAPIView):
    # def get(self,request):
        # serializers = WarehouseSerializers(queryset,many=True)
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializers
    #     return HttpResponse(serializer_class)
    # def post(self,request):
    #     warehouse_data = WarehouseSerializers(data=request.data)
    #     if not warehouse_data.is_valid():
    #         return Response('sai du lieu', status=status.HTTP_400_BAD_REQUEST)
    #     name = warehouse_data.data['name']
    #     wh = Warehouse.objects.create(name=name)
    #     return Response(data=wh.warehouse_id,status=status.HTTP_201_CREATED)

class WarehouseView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializers

class ShelfView(generics.ListCreateAPIView):
    queryset = Shelf.objects.all()
    serializer_class = ShelfSerializers

class ShelfView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shelf.objects.all()
    serializer_class = ShelfSerializers

class BoxCaseView(generics.ListCreateAPIView):
    queryset = BoxCase.objects.all()
    serializer_class = BoxCaseSerializers

class BoxCaseView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoxCase.objects.all()
    serializer_class = BoxCaseSerializers

class PortfolioView(generics.ListCreateAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializers

class PortfolioView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializers

class FolderView(generics.ListCreateAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializers

class FolderView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializers

class DocumentView(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializers

class DocumentView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializers

class WatchlistView(generics.ListCreateAPIView):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializers

class WatchlistView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializers












# class ShelfView(APIView):
#     def get(self,request):
#         queryset = Shelf.objects.all()
#         serializers = ShelfSerializers(queryset,many=True)
#         return Response(serializers.data)
#     def post(self,request):
#         shelf_data = ShelfSerializers(data=request.data)
#         if not shelf_data.is_valid():
#             return Response('sai du lieu', status=status.HTTP_400_BAD_REQUEST)
#         name = shelf_data.data['name']
#         sh = Shelf.objects.create(name=name)
#         return Response(data=sh.shelf_id,status=status.HTTP_201_CREATED)
    
# class BoxCaseView(APIView):
#     def get(self,request):
#         queryset = BoxCase.objects.all()
#         serializers = BoxCaseSerializers(queryset,many=True)
#         return Response(serializers.data)
#     def post(self,request):
#         boxcase_data = BoxCaseSerializers(data=request.data)
#         if not boxcase_data.is_valid():
#             return Response('sai du lieu', status=status.HTTP_400_BAD_REQUEST)
#         name = boxcase_data.data['name']
#         description = boxcase_data.data['description']
#         shelf_code = boxcase_data.data['shelf_code']
#         bc = BoxCase.objects.create(name=name,description=description,shelf_code=shelf_code)
#         return Response(data=bc.boxcase_id,status=status.HTTP_201_CREATED)

    
