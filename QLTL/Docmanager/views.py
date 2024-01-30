# from django.shortcuts import render
# from rest_framework import status,generics,serializers,permissions
# from rest_framework.views import APIView, View
# from rest_framework.response import Response
# from .model_serializers import BaseSerializers,BoxCaseSerializers,ShelfSerializers,FolderSerializers,PortfolioSerializers,DocumentSerializers,WarehouseSerializers,WatchlistSerializers
# from .models import Base,BoxCase,Shelf,Document,Portfolio,Warehouse,Folder,Watchlist

# # Create your views here.

# class BoxCaseView(generics.CreateAPIView):
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

# class ShelfView(generics.CreateAPIView):
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

# class WarehouseView(generics.CreateAPIView):
#     def get(self,request):
#         queryset = Warehouse.objects.all()
#         serializers = WarehouseSerializers(queryset,many=True)
#         return Response(serializers.data)
#     def post(self,request):
#         warehouse_data = WarehouseSerializers(data=request.data)
#         if not warehouse_data.is_valid():
#             return Response('sai du lieu', status=status.HTTP_400_BAD_REQUEST)
#         name = warehouse_data.data['name']
#         wh = Warehouse.objects.create(name=name)
#         return Response(data=wh.warehouse_id,status=status.HTTP_201_CREATED)
    
