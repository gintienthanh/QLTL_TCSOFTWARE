from django.shortcuts import render
from rest_framework import status,generics,serializers,permissions
from rest_framework.views import APIView, View
from rest_framework.response import Response
from django.http import HttpResponse,JsonResponse
from .model_serializers import *
from .models import *
from django.http import FileResponse
from django.shortcuts import get_object_or_404
import mimetypes
import shutil
import tkinter as tk
from tkinter import filedialog
# Create your views here.
# class WarehouseView(APIView):
#     def get(self,request):
#         queryset = Warehouse.objects.all()
#         serializers = WarehouseSerializers(queryset,many=True)
#         return HttpResponse(serializers)
#     def post(self,request):
#         # warehouse_data = WarehouseSerializers(data=request.data)
#         # if warehouse_data.is_valid():
#         #     warehouse_data.save()
#         #     arr = [warehouse_data.data]
#         #     return Response(arr, status=status.HTTP_201_CREATED)
#         # return Response(warehouse_data.errors, status=status.HTTP_400_BAD_REQUEST)
#         warehouse_data = WarehouseSerializers(data=request.data)
#         if warehouse_data.is_valid():
#             print(User.objects.get(id=warehouse_data.data["owner"]))
#             obj = Warehouse(name = warehouse_data.data['name'],warehouse_code=warehouse_data.data['warehouse_code'],owner=User.objects.get(id=warehouse_data.data["owner"]))
#             obj.save()
#             return Response(data=warehouse_data.data,status=status.HTTP_201_CREATED)
#         return Response('sai du lieu', status=status.HTTP_400_BAD_REQUEST)
    
class WarehouseView(generics.ListCreateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializers

class Warehouse_IDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializers
    lookup_field = 'warehouse_id'

class ShelfView(generics.ListCreateAPIView):
    queryset = Shelf.objects.all()
    serializer_class = ShelfSerializers

class Shelf_IDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shelf.objects.all()
    serializer_class = ShelfSerializers
    lookup_field = 'shelf_id'


class BoxCaseView(generics.ListCreateAPIView):
    queryset = BoxCase.objects.all()
    serializer_class = BoxCaseSerializers

class BoxCase_IDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoxCase.objects.all()
    serializer_class = BoxCaseSerializers
    lookup_field = 'boxcase_id'


class DocumentView(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializers

class Document_IDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializers
    lookup_field = 'document_id'


class PortfolioView(generics.ListCreateAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializers

class Portfolio_IDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializers
    lookup_field = 'portfolio_id'


class FolderView(generics.ListCreateAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializers

class Folder_IDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializers
    lookup_field = 'folder_id'


class WatchlistView(generics.ListCreateAPIView):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializers

class Watchlist_IDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializers
    lookup_field = 'watchlist_id'

class DownloadFile(APIView):
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() 
    lookup_field = 'document_id'
    def choose_download_path(self):
        # Hiển thị hộp thoại chọn đường dẫn lưu trữ
        download_path = filedialog.askdirectory()
        return download_path
    def get(self, request, document_id,format=None):
        file = Document.objects.get(document_id=document_id)
        file_path = file.files.path
        content_type, encoding = mimetypes.guess_type(file_path)
        content_type = content_type or 'application/octet-stream'

        response = HttpResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file.files.name}"'
        # shutil.copy2(file_path, save_path)
        return response