from django.shortcuts import render
from rest_framework import status,generics,serializers,permissions,authentication
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
from rest_framework import filters
import pandas as pd
import zipfile
from io import BytesIO
import openpyxl

# Create your views here.

class PortfolioList(APIView):
    def get(self, request):
        portfolios = Portfolio.objects.all()
        serializer = PortfolioSerializers(portfolios, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PortfolioSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PortfolioUpdate(APIView):
    def get_object(self, pk):
        try:
            return Portfolio.objects.get(pk=pk)
        except Portfolio.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def put(self, request, pk):
        portfolio = self.get_object(pk)
        serializer = PortfolioSerializers(portfolio, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        portfolio = self.get_object(pk)
        serializer = PortfolioSerializers(portfolio, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        portfolio = self.get_object(pk)
        portfolio.is_deleted = True
        portfolio.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class PortfolioFilter(generics.ListAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializers
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    
class DocumentList(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializers
    
class DocumentUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializers
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
 
class DocumentFilter(generics.ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializers
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']   
    
class FolderList(APIView):
    def get(self, request):
        folders = Folder.objects.filter(is_delete = False)
        serializer = FolderSerializers(folders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FolderSerializers(data=request.data)
        if serializer.is_valid():
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
            # Lưu tệp tin
                item = Folder.objects.create(type='File', files=uploaded_file)
                item.save()
                serializer.save()
            else:
                # Lưu thư mục
                item = Folder.objects.create(type='Folder')
                item.save()
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FolderUpdate(APIView):
    def get_object(self, pk):
        try:
            return Folder.objects.get(pk=pk)
        except Folder.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    
    def put(self, request, pk):
        folder = self.get_object(pk)
        serializer = FolderSerializers(folder, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        folder = self.get_object(pk)
        serializer = FolderSerializers(folder, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        folder = self.get_object(pk)
        folder.is_deleted = True
        folder.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FolderParentView(APIView):
    def get(self,request,parent_folder):
        try:
            queryset_folder = Folder.objects.filter(parent_folder = parent_folder)
            serializer_folder = FolderSerializers(queryset_folder,many=True)
            response = {
                "status":200,
                "data": {
                    "folder": serializer_folder.data,  
                }
            }
            return Response(response,status=status.HTTP_200_OK)
        except:
            return Response({'status':400},status=status.HTTP_400_BAD_REQUEST)

    
class FolderFilter(generics.ListAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializers
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    

class WarehouseList(APIView):
    def get(self, request):
        warehouses = Warehouse.objects.all()
        serializer = WarehouseSerializers(warehouses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WarehouseSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WarehouseUpdate(APIView):
    def get_object(self, pk):
        try:
            return Warehouse.objects.get(pk=pk)
        except Warehouse.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def put(self, request, pk):
        warehouse = self.get_object(pk)
        serializer = WarehouseSerializers(warehouse, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        warehouse = self.get_object(pk)
        serializer = WarehouseSerializers(warehouse, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):
        warehouse = self.get_object(pk)
        warehouse.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class WareHouseFilter(generics.ListAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializers
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class WatchList(APIView):
    def get(self, request):
        watchlists = Watchlist.objects.all()
        serializer = WatchlistSerializers(watchlists, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WatchlistSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            watchlist = Watchlist.objects.get(pk=pk)
        except Watchlist.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = WatchlistSerializers(watchlist, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            watchlist = Watchlist.objects.get(pk=pk)
        except Watchlist.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        watchlist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class DownloadConvertAPIView(generics.RetrieveAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializers

    def retrieve(self, request, *args, **kwargs):
        portfolio = self.get_object()

        # Tạo DataFrame từ thông tin hồ sơ
        portfolio_data = {
            'title': portfolio.title,
            'identification_code': portfolio.identification_code,
            'classification_id': portfolio.classification_id,
            'retention_period': portfolio.retention_period,
            'usage_policy': portfolio.usage_policy,
            'start_date': portfolio.start_date,
            'end_date': portfolio.end_date,
            'physical_condition': portfolio.physical_condition,
            'box_case': portfolio.box_case.name,
            'keywords': portfolio.keywords,
            'annotation': portfolio.annotation,
            'barcode': portfolio.barcode,
            'status': portfolio.get_status_display()
        }
        portfolio_df = pd.DataFrame([portfolio_data])

        # Tạo file Excel chứa thông tin hồ sơ trong bộ nhớ
        portfolio_excel_file = BytesIO()
        with pd.ExcelWriter(portfolio_excel_file, engine='openpyxl') as writer:
            portfolio_df.to_excel(writer, index=False)
        portfolio_excel_file.seek(0)

        # Tạo file Excel chứa thông tin các tài liệu trong bộ nhớ
        documents = Document.objects.filter(portfolio=portfolio)
        documents_data = []
        for document in documents:
            document_data = {
                'name': document.name,
                'box_case': document.box_case.name,
                'path': document.path,
                'folder': document.folder.name if document.folder else None,
                'border_frame': document.border_frame,
                'color': document.color,
                'usage_mode': document.usage_mode,
                'storage_code': document.storage_code,
                'document_expiration': document.document_expiration,
                'image_title': document.image_title,
                'date': document.date,
                'physical_status': document.physical_status,
                'note': document.note
            }
            documents_data.append(document_data)
        documents_df = pd.DataFrame(documents_data)

        documents_excel_file = BytesIO()
        with pd.ExcelWriter(documents_excel_file, engine='openpyxl') as writer:
            documents_df.to_excel(writer, index=False)
        documents_excel_file.seek(0)

        zip_file = BytesIO()
        with zipfile.ZipFile(zip_file, 'w') as zf:
            zf.writestr('portfolio_info.xlsx', portfolio_excel_file.getvalue())
            zf.writestr('documents_info.xlsx', documents_excel_file.getvalue())
        zip_file.seek(0)

        response = HttpResponse(zip_file.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=data.zip'
        
        return response

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

class Search(View):
    def post(sefl,req):
        searched = req.POST['searched']
        keys = Document.objects.filter(name__contains = searched)
        return render(req, 'home/search.html', {'searched':searched,'keys':keys})