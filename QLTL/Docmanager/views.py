from django.shortcuts import render
from rest_framework import status,generics,serializers,permissions
from rest_framework.views import APIView, View
from rest_framework.response import Response
from django.http import HttpResponse,JsonResponse
from .model_serializers import *
from .models import *
from django.http import FileResponse
import mimetypes
import shutil
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import zipfile
from io import BytesIO
import openpyxl
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
    
class WarehouseView(APIView):
    def get(self,req):
        queryset = Warehouse.objects.all()
        serializer_class = WarehouseSerializers
        return Response(serializer_class.data, status=200)

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

class FolderChildView(APIView):
    def get(self,request,child_folder):
        try:
            queryset_folder = Folder.objects.filter(child_folder = child_folder)
            serializer_folder = FolderSerializers(queryset_folder,many=True)
            queryset_document = Document.objects.filter(folder__child_folder = child_folder)
            print(queryset_document)
            # if queryset_document is None:
            #     serializer_document = DocumentSerializers(queryset_document,many=True)
            #     return Response(serializer_folder.data + serializer_document.data)
            serializer_document = DocumentSerializers(queryset_document,many=True)
            response = {
                "status":200,
                "data": {
                    "folder": serializer_folder.data, 
                    "document": serializer_document.data,
                }
            }
            return Response(response,status=status.HTTP_200_OK)
        except:
            return Response({'status':400},status=status.HTTP_400_BAD_REQUEST)

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

class Downloadfolder(generics.RetrieveAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializers
    lookup_field = 'folder_id'

    def retrieve(self, request, *args, **kwargs):
        folder = self.get_object()
        data = {
            'name': folder.name,
            'boxcase_id': getattr(folder.boxcase, 'name', None),
            'shelf_id': getattr(folder.shelf, 'name', None),
        }
        df = pd.DataFrame([data])

        excel_file = BytesIO()
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        excel_file.seek(0)

        zip_file = BytesIO()
        with zipfile.ZipFile(zip_file, 'w') as zf:
            zf.writestr('data.xlsx', excel_file.getvalue())
        zip_file.seek(0)

        response = HttpResponse(zip_file.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=data.zip'
        return response

class Search(View):
    def post(sefl,req):
        searched = req.POST['searched']
        keys = Document.objects.filter(name__contains = searched)
        return render(req, 'home/search.html', {'searched':searched,'keys':keys})