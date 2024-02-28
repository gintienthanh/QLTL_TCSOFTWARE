from django.shortcuts import render
from rest_framework import status,generics,serializers,permissions,authentication
from rest_framework.views import APIView, View
from rest_framework.response import Response
from django.http import HttpResponse,JsonResponse
from .model_serializers import *
from .models import *
from django.http import FileResponse
import mimetypes
import tkinter as tk
from tkinter import filedialog
from rest_framework import filters
from Docmanager.permissions import CheckOwnerFactory, CheckSharedGroupdFactory
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
import mimetypes
import pandas as pd
import os
import zipfile
from io import BytesIO
from django.core.files.storage import default_storage
from django.db.models import Q
# Create your views here.
from django.core.files.storage import FileSystemStorage
import uuid
class PortfolioSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 1000  
class FolderSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 1000  
class WarehouseSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 1000  
class ShareSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 1000  

class WatchlistSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 1000  




class PortfolioList(APIView):
    permission_classes = [permissions.IsAuthenticated]
   
    def get(self, request, *args, **kwargs):
        paginator = PortfolioSetPagination()
        title_query = request.GET.get('title', None)  
       
        portfolio = Portfolio.objects.filter(is_delete=False)
    
        if title_query: 
             portfolio = portfolio.filter(title__icontains=title_query)
        
    
        result_page = paginator.paginate_queryset(portfolio, request)
        serializer = PortfolioSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = PortfolioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PortfolioUpdate(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Portfolio.objects.get(pk=pk)
        except Portfolio.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
        
    def get(self, request, pk):
        portfolio = self.get_object(pk)
        serializer = PortfolioSerializer(portfolio)
        return Response(serializer.data)

    def put(self, request, pk):
        portfolio = self.get_object(pk)
        serializer = PortfolioSerializer(portfolio, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        portfolio = self.get_object(pk)
        serializer = PortfolioSerializer(portfolio, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        portfolio = self.get_object(pk)
        serializer = PortfolioSerializer(portfolio, 
            data =
            {
                'is_delete': True,
                
            }, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PortfolioFilter(generics.ListAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['title']

    
    
class DocumentList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
class DocumentUpdate(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
 
class DocumentFilter(generics.ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['name']



class FolderList(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            paginator=FolderSetPagination()
            name_query = request.GET.get('name', None)  
            parent_folder = request.GET.get('parent_folder')
            folder = Folder.objects.filter(is_delete=False)
            if not parent_folder:
                folder = Folder.objects.filter(parent_folder=None)
            else:
                folder = Folder.objects.filter(parent_folder=parent_folder)
            if name_query: 
                folder = folder.filter(name__icontains=name_query)
            
            result_page = paginator.paginate_queryset(folder, request)
            serializer = FolderSerializer(result_page, many=True)
            data = {
                    'status': '200',
                    'message':' found successfully',
                    'pagination': {
                        'total_pages': paginator.page.paginator.num_pages,
                        'current_page': paginator.page.number,
                        'next_page': paginator.get_next_link(),
                        'previous_page': paginator.get_previous_link(),
                    },
                    'data': serializer.data,
                    
                }
            return Response(data, status=status.HTTP_200_OK)
        except:
            return Response({'status':400},status=status.HTTP_400_BAD_REQUEST)
        
    def extract_and_convert_to_integer(self,name,data):
        start_index = name.rfind('(')
        end_index = name.rfind(')')
        if start_index != -1 and end_index != -1 and start_index < end_index:
            try:
                name_list = []
                for i in data:
                    name_list.append(i['name'])
                for i in name_list:
                    if name in name_list:
                        substring = name[start_index+1:end_index]
                        integer_value = int(substring)
                        integer_value += 1
                        name_lst = list(name)
                        name_lst[start_index + 1] = str(integer_value)
                        new_name = ''.join(name_lst)
                        name = new_name
                return name
            except ValueError:
                return name
    def post(self, request):
        serializer = FolderSerializer(data=request.data)
        files = request.FILES.getlist('files')
        name = request.POST.get('name')
        name = name.rstrip()
        parent_folder = request.POST.get('parent_folder')
        if serializer.is_valid():
            if parent_folder:
                queryset = Folder.objects.filter(parent_folder = parent_folder)
            else:
                queryset = Folder.objects.filter(parent_folder = None)
            serializer_db = FolderSerializer(queryset,many=True)
            data = serializer_db.data
            if files:
                files_list = []
                name_list = []
                file_name_list = []
                for i in data:
                    name_list.append(i['name'])
                for file in files:
                    name = file.name
                    for i in name_list:
                        file_name_list.append(i)
                    start_index = name.rfind('.')
                    name_default = name[:start_index] + "(1)" + name[start_index:]
                    files_list.append(file)
                    if name not in name_list: 
                        print(1)
                        serializer.save(type='File', files=file,file_size = file.size, path = file, name = name)
                    elif name_default not in name_list and name in name_list:
                        print(2)
                        serializer.save(type='File', files=file,file_size = file.size, path = file, name = name_default)
                    elif name_default in name_list and name in name_list:
                        newname = self.extract_and_convert_to_integer(name_default,data)
                        print(newname)
                        serializer.save(type='File', files=file,file_size = file.size, path = file, name = newname)
            else:
                name_list = []
                for i in data:
                    name_list.append(i['name'])
                if name not in name_list: 
                    serializer.save(type='Folder',file_size = 0,name = name)
                elif name + " (1)" not in name_list and name in name_list:
                    name = name + " (1)"
                    serializer.save(type='Folder',file_size = 0,name = name)
                elif name + " (1)" in name_list and name in name_list:
                    name = name + " (1)"
                    newname = self.extract_and_convert_to_integer(name,data)
                    serializer.save(type='Folder',file_size = 0,name = newname)
            response = {
                "status":200,
                "data": {
                    "folder": serializer.data,  
                }
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response({'status':400}, status=status.HTTP_400_BAD_REQUEST)
            

class FolderUpdate(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def get_object(self, pk):
        try:
            return Folder.objects.get(pk=pk)
        except Folder.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def get(self, request, pk):
        folder = self.get_object(pk)
        serializer = FolderSerializer(folder)
        return Response(serializer.data)
    
    def put(self, request, pk):
        folder = self.get_object(pk)
        serializer = FolderSerializer(folder, data=request.data)
        uploaded_file = request.FILES.get('files')
        files = request.FILES.getlist('files[]')
        name = request.POST.get('name')
        name = name.rstrip()
        parent_folder = request.POST.get('parent_folder')
        if serializer.is_valid():
            if files:
                # Lưu danh sách các tệp tin
                queryset = Folder.objects.filter(parent_folder = parent_folder)
                serializer_db = FolderSerializer(queryset,many=True)
                data = serializer_db.data
                files_list = []
                for file in files:
                    file_path = default_storage.save(file.name, file)
                    name = file.name
                    files_list.append(file)
                    for i in data:
                        name_list.append(i['name'])
                    if name not in name_list: 
                        serializer.save(type='File', files=uploaded_file,file_size = uploaded_file.size, path = file_path, name = name)
                    elif name + " (1)" not in name_list and name in name_list:
                        name = name + " (1)"
                        serializer.save(type='File', files=uploaded_file,file_size = uploaded_file.size, path = file_path, name = name)
                    elif name + " (1)" in name_list and name in name_list:
                        name = name + " (1)"
                        newname = self.extract_and_convert_to_integer(name,data)
                        serializer.save(type='File', files=uploaded_file,file_size = uploaded_file.size, path = file_path, name = name)
            elif uploaded_file:
                    queryset = Folder.objects.filter(parent_folder = parent_folder)
                    serializer_db = FolderSerializer(queryset,many=True)
                    data = serializer_db.data
                    file_path = default_storage.save(uploaded_file.name, uploaded_file)
                    name = uploaded_file.name
                    name_list = []
                    for i in data:
                        name_list.append(i['name'])
                    if name not in name_list: 
                        serializer.save(type='File', files=uploaded_file,file_size = uploaded_file.size, path = file_path, name = name)
                    elif name + " (1)" not in name_list and name in name_list:
                        name = name + " (1)"
                        serializer.save(type='File', files=uploaded_file,file_size = uploaded_file.size, path = file_path, name = name)
                    elif name + " (1)" in name_list and name in name_list:
                        name = name + " (1)"
                        newname = self.extract_and_convert_to_integer(name,data)
                        serializer.save(type='File', files=uploaded_file,file_size = uploaded_file.size, path = file_path, name = name)
            else:
                queryset = Folder.objects.filter(parent_folder = parent_folder)
                serializer_db = FolderSerializer(queryset,many=True)
                data = serializer_db.data
                name_list = []
                for i in data:
                    name_list.append(i['name'])
                if name not in name_list: 
                    serializer.save(type='Folder',file_size = 0,name = name)
                elif name + " (1)" not in name_list and name in name_list:
                    name = name + " (1)"
                    serializer.save(type='Folder',file_size = 0,name = name)
                elif name + " (1)" in name_list and name in name_list:
                    name = name + " (1)"
                    newname = self.extract_and_convert_to_integer(name,data)
                    serializer.save(type='Folder',file_size = 0,name = newname)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        folder = self.get_object(pk)
        serializer = FolderSerializer(folder, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        folder = self.get_object(pk)
        folder.is_delete = True
        serializer = FolderSerializer(folder, 
            data =
            {
                'is_delete': True,
            }, partial=True)
        if serializer.is_valid():
            queryset = Folder.objects.filter(parent_folder = pk)
            serializer_db = FolderSerializer(queryset,many=True)
            data = serializer_db.data
            for i in data:
                self.delete(request,i['id'])
            folder.save()
            return Response({'status':200},status=status.HTTP_200_OK)
        return Response({'status':400}, status=status.HTTP_400_BAD_REQUEST)

# class FolderDeletes(APIView):
#     def delete(self, request,pk, *args, **kwargs):
#         folder_list = folder_id.split(',')
#         for folder_id in folder_list:
#             try:
#                 folder = Folder.objects.get(id=int(folder_id))
#                 folder.is_delete = True
#                 folder.save()
#             except Folder.DoesNotExist:
#                 pass
#         return Response(status=status.HTTP_204_NO_CONTENT)


class FolderFilter(generics.ListAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['name','file_size','parent_folder']

class ShareList(generics.ListCreateAPIView):
    queryset = Share.objects.all()
    serializer_class = ShareSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('owner','create_by','document','folder')
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        elif self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
        
    def get(self, request):
        paginator = ShareSetPagination
        share = Share.objects.filter(is_delete=False)
        serializer = ShareSerializer(share, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            serializer = ShareSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    share = Share.objects.get(
                        folder=serializer.validated_data.get('folder'),
                        document=serializer.validated_data.get('document'),
                        create_by=request.user,
                        owner=serializer.validated_data.get('owner'),
                        type=serializer.validated_data.get('type')
                    )
                    share.create_by = request.user
                    share.save()
                    serializer = ShareSerializer(share)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except Share.DoesNotExist:
                    serializer.save(create_by=request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        

class ShareUpdate(APIView):
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class ShareList(generics.ListCreateAPIView):
#     queryset = Share.objects.all()
#     serializer_class = ShareSerializer
#     filter_backends = [filters.DjangoFilterBackend]
#     filterset_fields = ('owner', 'folder', 'document')

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         share = Share.objects.filter(folder=serializer.validated_data.get('folder'),
#                                      document=serializer.validated_data.get('document'),
#                                      create_by = request.user,
#                                      owner = serializer.validated_data.get('owner'),
#                                      type = serializer.validated_data.get('type')
#                                      )
#         if share:
#             share.update(create_by=request.user)
#             updated_share = share.first()
#             serializer = self.get_serializer(updated_share)
#         else:
#             serializer.save(create_by=request.user)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# class ShareUpdate(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Share.objects.all()
#     serializer_class = ShareSerializer
#     permission_classes = [CheckSharedGroupdFactory(Share(), 'Chỉnh sửa') | CheckOwnerFactory(Share())]



    
#     def delete(self, request, *args, **kwargs):
#         instance = self.get_object()
#         instance.delete(delete_by=request.user)
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class ShareFilter(filters.FilterSet):
#     class Meta:
#         model = Share
#         fields = ('owner', 'folder', 'document')
class WarehouseList(APIView):
    permission_classes = [IsAuthenticated]
    
    # def get(self, request):
    #     warehouses = Warehouse.objects.all()
    #     serializer = WarehouseSerializer(warehouses, many=True)
    #     return Response(serializer.data)
    def get(self, request, *args, **kwargs):
        paginator = WatchlistSetPagination
        type_warehouse = request.GET.get('type_warehouse')

        if type_warehouse == 'shelf':
            warehouse = Warehouse.objects.filter(type_warehouse='shelf',is_delete=False)
        elif type_warehouse == 'warehouse':
            warehouse = Warehouse.objects.filter(type_warehouse='warehouse', is_delete=False)
        elif type_warehouse == 'boxcase':
            warehouse = Warehouse.objects.filter(type_warehouse='boxcase', is_delete=False)
        else:
            return Response({"error": "Invalid type_warehouse value"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WarehouseSerializer(warehouse, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = WarehouseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WarehouseUpdate(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Warehouse.objects.get(pk=pk)
        except Warehouse.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def get(self, request, pk):
        warehouse = self.get_object(pk)
        serializer = WarehouseSerializer(warehouse)
        return Response(serializer.data)
    def put(self, request, pk):
        warehouse = self.get_object(pk)
    
        # Copy request data to remove 'type_warehouse' field
        modified_data = request.data.copy()
        if 'type_warehouse' in modified_data:
            del modified_data['type_warehouse']
    
        serializer = WarehouseSerializer(warehouse, data=modified_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        warehouse = self.get_object(pk)
    
        # Copy request data to remove 'type_warehouse' field
        modified_data = request.data.copy()
        if 'type_warehouse' in modified_data:
            del modified_data['type_warehouse']
    
        serializer = WarehouseSerializer(warehouse, data=modified_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):
        warehouse = self.get_object(pk)
        serializer = WarehouseSerializer(warehouse, 
            data =
            {
                'is_delete': True,
                
            }, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WarehouseFilter(generics.ListAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['name','type_warehouse', 'parent_warehouse']



class WatchList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        paginator = WatchlistSetPagination
        watchlist = Watchlist.objects.filter(is_delete=False)
        serializer = WatchListSerializer(watchlist, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WatchlistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class WatchListUpdate(APIView):
    def get_object(self, pk):
        try:
            return Watchlist.objects.get(pk=pk)
        except Watchlist.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def get(self, request, pk):
        watchlist = self.get_object(pk)
        serializer = WatchListSerializer(watchlist)
        return Response(serializer.data)

    def put(self, request, pk):
        watchlist = self.get_object(pk)
        serializer = WatchListSerializer(watchlist, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        watchlist = self.get_object(pk)
        serializer = WatchListSerializer(watchlist, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        watchlist = self.get_object(pk)
        serializer = WatchListSerializer(watchlist, 
            data =
            {
                'is_delete': True,
                
            }, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DownloadFile(APIView):
    lookup_field = 'folder_id'
    def get(self, request, folder_id,format=None):
        try:
            file = Folder.objects.get(pk=folder_id)
            file_path = file.files.path
            print(file.name)
            print(123123)
            content_type, encoding = mimetypes.guess_type(file_path)
            content_type = content_type or 'application/octet-stream'
            response = HttpResponse(open(file_path, 'rb'), content_type=content_type)
            # Tạo response từ tệp tin
            response['Content-Disposition'] = f'attachment; filename="{file.name}"'
            # shutil.copy2(file_path, save_path)
            return response
        except Folder.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

class DownloadConvertAPIView(generics.RetrieveAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer

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
    lookup_field = 'folder_id'
    def get(self, request, folder_id,format=None):
        try:
            file = Folder.objects.get(pk=folder_id)
            file_path = file.files.path
            filename = file.name
            content_type, encoding = mimetypes.guess_type(file_path)
            content_type = content_type or 'application/octet-stream'
            response = HttpResponse(open(file_path, 'rb'), content_type=content_type)
            # Tạo response từ tệp tin
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            # shutil.copy2(file_path, save_path)
            return response
        except Folder.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

class DownloadFolder(APIView):
    def get(self,request,pk):
        try:
            folder = Folder.objects.get(pk=pk)
        except Folder.DoesNotExist:
            return HttpResponse('Thư mục không tồn tại')
        zip_file_name = folder.name + '.zip'
        # with tempfile.NamedTemporaryFile(delete=False) as temp_zip_file:
        #     with zipfile.ZipFile(temp_zip_file, 'w') as zipf:
            # self.add_folder_to_zip(zipf, folder,pk)
        # with open(temp_zip_file.name, 'rb') as zip_file:
        #     response = HttpResponse(zip_file.read(), content_type='application/zip')
        #     response['Content-Disposition'] = f'attachment; filename="{zip_file_name}"'
        #     return response
        zip_buffer = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
        folderchild = Folder.objects.filter(parent_folder = pk)
        serializer = FolderSerializer(folderchild,many=True)
        for i in serializer.data:
            folder = i['id']
            print(folder)
            if i['type'] == 'File':
                    file_path = 'files' + i['path']
                    name = i['name']
                    print(file_path)
                    content_type, encoding = mimetypes.guess_type(file_path)
                    content_type = content_type or 'application/octet-stream'
                    response = HttpResponse(open(file_path, 'rb'), content_type=content_type)
                    # Tạo response từ tệp tin
                    response['Content-Disposition'] = f'attachment; filename="{name}"'
                    # shutil.copy2(file_path, save_path)
                    
        zip_buffer.close()

        with open(zip_file_name, 'rb') as zip_file:
            response = HttpResponse(zip_file.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{zip_file_name}"'
            return response

        
    def add_folder_to_zip(self, zipf, folder,pk):
        queryset = Folder.objects.filter(parent_folder = pk)
        serializer = FolderSerializer(queryset,many=True)
        for i in serializer.data:
            folder = i['id']
            print(folder)
            try:
                if i['type'] == 'File':
                    file = Folder.objects.get(pk=pk)
                    file_path = file.files.path
                    content_type, encoding = mimetypes.guess_type(file_path)
                    content_type = content_type or 'application/octet-stream'
                    response = HttpResponse(open(file_path, 'rb'), content_type=content_type)
                    # Tạo response từ tệp tin
                    response['Content-Disposition'] = f'attachment; filename="{file.files.name}"'
                    print(file_path)
                    # shutil.copy2(file_path, save_path)
                    pk = folder
                    self.add_folder_to_zip(zipf,folder,pk)
                else:
                    pk = folder
                    self.add_folder_to_zip(zipf,folder,pk)
            except:
                pass

            # file_path = file.get_absolute_file_path()  # Đường dẫn tới tệp tin
            # zipf.write(file_path, os.path.relpath(file_path, folder.get_absolute_folder_path()))

class Search(View):
    def post(sefl,req):
        searched = req.POST['searched']
        keys = Document.objects.filter(name__contains = searched)
        return render(req, 'home/search.html', {'searched':searched,'keys':keys})