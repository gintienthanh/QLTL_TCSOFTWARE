import datetime
import os
import shutil
from django.conf import settings
from django.shortcuts import render
from rest_framework import status,generics,serializers,permissions,authentication,filters
from rest_framework.views import APIView, View
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse,JsonResponse
from .model_serializers import *
from .models import *
from django.http import FileResponse
import mimetypes
import tkinter as tk
from tkinter import filedialog
from Docmanager.permissions import CheckOwnerFactory, CheckSharedGroupdFactory
from .model_serializers import*
from .models import*
from django_filters import rest_framework as filters
import mimetypes
import pandas as pd
from io import BytesIO
import zipfile
from django.core.files.storage import default_storage
from django.utils import timezone
from django.db.models import F, Case, When, Value, CharField
from django.db.models.functions import Coalesce
import shutil, re
from datetime import datetime
# Create your views here.

class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        next_page = self.get_next_link()
        previous_page = self.get_previous_link()
        total_pages = self.page.paginator.num_pages
        current_page = self.page.number
        total_count = self.page.paginator.count
        return Response({
            "status": "200",
            "message": " found successfully",
            "pagination": {
                "count": total_count,
                "total_pages": total_pages,
                "current_page": current_page,
                "next_page": next_page,
                "previous_page": previous_page,
                },
            "data": data,
        })
class PortfolioSetPagination(CustomPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000  
    
class FolderSetPagination(CustomPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000   
class WarehouseSetPagination(CustomPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 1000  
class ShareSetPagination(CustomPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000  

class WatchlistSetPagination(CustomPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000
class DocumentSetPagination(CustomPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000

#######PORTFOLIO######

class PortfolioFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    usage_policy = filters.CharFilter(field_name='usage_policy', lookup_expr='icontains')
    
    class Meta:
        model = Portfolio
        fields = ['title', 'usage_policy']
class PortfolioListCreate(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Portfolio.objects.annotate(
    compare_time=Coalesce(
        Case(
            When(created_at__gt=F('updated_at'), then=F('created_at')),
            default=F('updated_at'),
            output_field=CharField()
        ),
        Case(
            When(created_at__gt=F('created_at'), then=F('updated_at')),
            default=F('created_at'),
            output_field=CharField()
        )
    )
).order_by('-compare_time')
    serializer_class = PortfolioSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = PortfolioFilter
    paginator = PortfolioSetPagination()
    
    def get_queryset(self):
        
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            queryset = queryset.filter(create_by=user, is_delete = False)
        return queryset 
    
    def post(self, request):
        serializer = PortfolioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':201,
                             'message':'created successfully',
                             'data':serializer.data}, 
                             status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class PortfolioUpdateDelete(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def get_object(self, pk):
        try:
            return Portfolio.objects.get(pk=pk)
        except Portfolio.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def get(self, request, pk):
        portfolio = self.get_object(pk)
        serializer = PortfolioSerializer(portfolio)
        return Response({'status':201,
                        'message':'found',
                        'data':serializer.data},status=status.HTTP_302_FOUND)


    def patch(self, request, pk):
        portfolio = self.get_object(pk)
        serializer = PortfolioSerializer(portfolio, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.validated_data['updated_at'] = timezone.now()
            serializer.validated_data['editor'] = timezone.now()
            serializer.save()
            return Response({'status':201,
                             'message':'created successfully',
                             'data':serializer.data},status=status.HTTP_200_OK)
        return Response({'status':400,
                        'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        instance = Portfolio.objects.get(pk=pk)
        instance.soft_delete(request)
        return Response({'status':200,
                             'message':'delete successfully'
                            })
#######DOCUMENT######
class DocumentFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Document
        fields = ['name', 'folder_id']

    

class DocumentListCreate(generics.ListCreateAPIView):

    permission_classes = [permissions.IsAuthenticated]
    queryset = Document.objects.annotate(
    compare_time=Coalesce(
        Case(
            When(created_at__gt=F('updated_at'), then=F('created_at')),
            default=F('updated_at'),
            output_field=CharField()
        ),
        Case(
            When(created_at__gt=F('created_at'), then=F('updated_at')),
            default=F('created_at'),
            output_field=CharField()
        )
    )
    ).order_by('-compare_time')
    serializer_class = DocumentSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = DocumentFilter
    paginator = DocumentSetPagination()
    
    def get_queryset(self):
        
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            queryset = queryset.filter(create_by=user, is_delete=False)
        return queryset 
    
    def post(self, request):
        serializer = PortfolioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['create_by'] = request.user   
            serializer.save()
            return Response({'status':201,
                             'message':'created successfully',
                             'data':serializer.data}, 
                             status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DocumentUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    #permission_classes = [CheckSharedGroupdFactory(Document(),'edit') | CheckOwnerFactory(Document())]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response({'status':200,'message':'destroyed'},status=status.HTTP_204_NO_CONTENT)


class FolderFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    
    class Meta:
        model = Folder
        fields = ['name', 'parent_folder','type']


class FolderListCreate(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Folder.objects.annotate(
    compare_time=Coalesce(
        Case(
            When(created_at__gt=F('updated_at'), then=F('created_at')),
            default=F('updated_at'),
            output_field=CharField()
        ),
        Case(
            When(created_at__gt=F('created_at'), then=F('updated_at')),
            default=F('created_at'),
            output_field=CharField()
        )
    )
    ).order_by('-compare_time')
    serializer_class = FolderSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = FolderFilter
    paginator = FolderSetPagination()
    
    def get_queryset(self):
        
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            parent_folder = self.request.GET.get('parent_folder')
            if not parent_folder:
                parent_folder = None
            queryset = queryset.filter(create_by=user, is_delete = False, parent_folder = parent_folder)
        return queryset
    def extract_and_convert_to_integer(self,name,name_list):
        while name in name_list:
            match = re.search(r'\((\d+)\)$|\((\d+)\)\.', name)
            if match.group(1):
                number_str = match.group(1)
                number = int(number_str)
                number += 1
                new_name = re.sub(r'\(\d+\)$', f'({number})', name)
            if match.group(2):
                number_str = match.group(2)
                number = int(number_str)
                number += 1
                new_name = re.sub(r'\((\d+)\)\.', f'({number}).', name)
            name = new_name
        return name
    def post(self, request):
        serializer = FolderSerializer(data=request.data,partial=True)
        files = request.FILES.getlist('files')
        name = request.data.get('name')
        parent_folder_id = request.data.get('parent_folder')
        user = request.user
        if name and name != '':
            name = name.rstrip()
        else:
            name = 'New Folder'
        if serializer.is_valid():
            if parent_folder_id:
                parent_folder = Folder.objects.get(id=parent_folder_id)
                owner = parent_folder.owner
                path = parent_folder.path
            else:
                parent_folder = None
                path = ''
                owner = user
            queryset = Folder.objects.filter(parent_folder=parent_folder)
            serializer_db = FolderSerializer(queryset, many=True)
            data = serializer_db.data
            name_list = [item['name'] for item in data]
            if files:
                type = 'File'
                for file in files:
                    name = file.name
                    start_index = name.rfind('.')
                    name_default = name[:start_index] + " (1)" + name[start_index:]
                    if name not in name_list: 
                        newname = name
                    elif name in name_list:
                        newname = self.extract_and_convert_to_integer(name_default,name_list)
                    serializer.save(type= type, files=file,file_size = file.size, path = path + newname, name = newname,parent_folder=parent_folder,create_by = user,owner=owner)
            else:
                type = 'Folder'
                name_default = name + " (1)"
                if name not in name_list: 
                    newname = name
                elif name in name_list:
                    newname = self.extract_and_convert_to_integer(name_default,name_list)
                serializer.save(type = type,file_size = 0,path = path + newname + "/",name = newname,parent_folder=parent_folder,create_by = user,owner=owner)
            response = {
                "status": 200,
                "message": "created successfully",
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response({'status':400}, status=status.HTTP_400_BAD_REQUEST)


class FolderUpdateDelete(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def __init__(self, *args, **kwargs):
        self.change_name = kwargs.pop('change_name', False)
        self.change_folder = kwargs.pop('change_folder', False)
        super().__init__(*args, **kwargs)

    def get_object(self, pk):
        try:
            return Folder.objects.get(pk=pk)
        except Folder.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def change(self,path,old_name,new_name):
        new_folder_path = path.replace(old_name,new_name)
        print(new_folder_path)
        return new_folder_path
    def patch(self, request, pk,change_name=False, change_folder=False):
        if change_name:
            return self.patch_change_name(request, pk)
        elif change_folder:
            return self.patch_change_folder(request, pk)
        else:
            return Response({'message': 'Yêu cầu không hợp lệ'})
    def patch_change_folder(self, request, pk):
        folder = self.get_object(pk)
        serializer = FolderSerializer(folder, data=request.data,partial=True)
        user = request.user
        parent_folder_id = request.data.get('parent_folder')
        if serializer.is_valid():
            if parent_folder_id:
                parent_folder = Folder.objects.get(id=parent_folder_id)
                path = parent_folder.path
            else:
                parent_folder_id = folder.parent_folder
                parent_folder = None
                path = ''
            if folder.type == "Folder":
                path = path + folder.name + "/"
            else:
                path = path + folder.name
            serializer.save(path = path,parent_folder=parent_folder,update_by = user)
            response = {
                "status":200,
                "message": "updated successfully",
                "data": {
                    "folder": serializer.data,  
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response({'status':400}, status=status.HTTP_400_BAD_REQUEST)
    def patch_change_name(self,request,pk):
        folder = self.get_object(pk)
        serializer = FolderSerializer(folder, data=request.data,partial=True)
        old_path = folder.path
        old_name = folder.name
        name = request.data.get('name')
        user = request.user
        if name and name != '':
            name = name.rstrip()
        else:
            name = folder.name
        parent_folder_id = folder.parent_folder_id
        if serializer.is_valid():
            if parent_folder_id:
                parent_folder = Folder.objects.get(id=parent_folder_id)
                path = parent_folder.path
            else:
                parent_folder = None
                path = ''
            queryset = Folder.objects.filter(parent_folder=parent_folder)
            serializer_db = FolderSerializer(queryset, many=True)
            data = serializer_db.data
            name_list = [item['name'] for item in data]
            name_default = name + " (1)"
            if name not in name_list:
                new_name = name
            else:
                new_name = FolderListCreate.extract_and_convert_to_integer(self,name_default,name_list)
            child_fol = Folder.objects.filter(path__startswith = old_path)
            new_path = path + new_name + '/'
            for i in child_fol:
                path_child = self.change(i.path,old_name,new_name)
                i.path = path_child
                i.save()
            serializer.save(path = new_path, name = new_name,update_by = user)
            response = {
                "status":200,
                "message": "updated successfully",
                "data": {
                    "folder": serializer.data,  
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response({'status':400}, status=status.HTTP_400_BAD_REQUEST)
class ShareFilter(filters.FilterSet):
    class Meta:
        model = Share
        fields = ['owner','create_by','document','folder']
   
class ShareList(generics.ListCreateAPIView):
    queryset = Share.objects.all()
    serializer_class = ShareSerializer
    filter_backends = (filters.DjangoFilterBackend)
    # filterset_fields = ('owner','create_by','document','folder')
    filterset_class = ShareFilter
    paginator = ShareSetPagination()
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            queryset = queryset.filter(create_by=user, is_delete=False)
        return queryset
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        elif self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()



    def post(self, request):
        # try:
        serializer = ShareSerializer(data=request.data)
        if serializer.is_valid():
            share = Share.objects.get(
                folder=serializer.validated_data.get('folder'),
                document=serializer.validated_data.get('document'),
                create_by=request.user,
                owner=serializer.validated_data.get('owner'),
                type=serializer.validated_data.get('type')
                )
            serializer = ShareSerializer(share)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
                
                
        # except Share.DoesNotExist:
        #     serializer.save(create_by=request.user)
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # except Exception as e:
        #     return Response({'status':400,'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class ShareUpdate(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [CheckSharedGroupdFactory(Share(),'edit') | CheckOwnerFactory(Share())]
    queryset = Share.objects.all()
    serializer_class = ShareSerializer

    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.updated_at = datetime.now()
        instance.editor = request.user
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete=True
        instance.delete_at=datetime.now() 
        instance.delete_by=request.user
        self.perform_update(instance)
        return Response({'status':200,'message':'destroyed'},status=status.HTTP_204_NO_CONTENT)
       

class  WarehouseFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    class Meta:
        model = Warehouse
        fields = ['name', 'parent_warehouse', 'type_warehouse'] 

class WarehouseListCreate(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Warehouse.objects.annotate(
    compare_time=Coalesce(
        Case(
            When(created_at__gt=F('updated_at'), then=F('created_at')),
            default=F('updated_at'),
            output_field=CharField()
        ),
        Case(
            When(created_at__gt=F('created_at'), then=F('updated_at')),
            default=F('created_at'),
            output_field=CharField()
        )
    )
    ).order_by('-compare_time')
    serializer_class = WarehouseSerializer 
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = WarehouseFilter
    paginator = WarehouseSetPagination()
    
        
    def post(self, request):
        try:
            serializer = WarehouseSerializer(data=request.data)
            id = request.data.get('parent_warehouse_id')
            if serializer.is_valid():
                 
                parent_warehouse =Warehouse.objects.get(id=id)    
                serializer.save(parent_warehouse=parent_warehouse)
                
                return Response({'status':201,
                                'message':'created successfully',
                                'data':serializer.data},status=status.HTTP_201_CREATED)
            return Response({'status':400,
                            'message':'created fail'},status=status.HTTP_400_BAD_REQUEST)
        except Warehouse.DoesNotExist:
            serializer.save()
            return Response({'status':201,
                            'message':'created successfully',
                            'data':serializer.data},status=status.HTTP_201_CREATED)
    
        
        except Exception as e:
            return Response({'status':400,
                            'message':'created fail'},status=status.HTTP_400_BAD_REQUEST)
            
            
            
######WAREHOUSE######

            
            
            

class WarehouseUpdateDelete(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def get_object(self, pk):
        try:
            return Warehouse.objects.get(pk=pk)
        except Warehouse.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def get(self, request, pk):
        warehouse = self.get_object(pk)
        serializer = WarehouseSerializer(warehouse)
        return Response({'status':200,
                             'message':'found successfully',
                             'data':serializer.data},status=status.HTTP_200_OK)


    def patch(self, request, pk):
        warehouse = self.get_object(pk)
    
        # Copy request data to remove 'type_warehouse' field
        modified_data = request.data.copy()
        if 'type_warehouse' in modified_data:
            del modified_data['type_warehouse']
    
        serializer = WarehouseSerializer(warehouse, data=modified_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':200,
                             'message':'update successfully'
                             },status=status.HTTP_200_OK)
        return Response({'status':400,
                             'message':'update fail'
                             },status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):
        warehouse = self.get_object(pk)
        
        if warehouse.type_warehouse == ChoicesTypeWarehouse.Shelf.value:
            # Soft delete the shelf and its associated boxcases
            warehouse.is_delete = True
            warehouse.delete_at = timezone.now()  # Cập nhật delete_at với ngày và giờ hiện tại
            warehouse.save()
            
            shelf_boxcases = Warehouse.objects.filter(parent_warehouse=warehouse)
            shelf_boxcases.update(is_delete=True, delete_at=timezone.now())  # Cập nhật delete_at cho các boxcase
            
        elif warehouse.type_warehouse == ChoicesTypeWarehouse.BoxCase.value:
            # Soft delete the boxcase and its associated shelf
            warehouse.is_delete = True
            warehouse.delete_at = timezone.now()  # Cập nhật delete_at với ngày và giờ hiện tại
            warehouse.save()
            
            shelf = warehouse.parent_warehouse
            shelf.is_delete = True
            shelf.delete_at = timezone.now()  # Cập nhật delete_at cho shelf
            shelf.save()
        
        else:
            # Soft delete the warehouse and its associated shelves and boxcases
            subwarehouses = warehouse.subwarehouse.all()
            for subwarehouse in subwarehouses:
                subwarehouse.is_delete = True
                subwarehouse.delete_at = timezone.now()  # Cập nhật delete_at cho các warehouse con
                subwarehouse.save()
            
            warehouse.is_delete = True
            warehouse.delete_at = timezone.now()  # Cập nhật delete_at với ngày và giờ hiện tại
            warehouse.save()
            return Response({'status':200,
                             'message':'delete successfully'},status=status.HTTP_200_OK)
        return Response({'status':400,
                             'message':'error'
                             },status=status.HTTP_400_BAD_REQUEST)


#######WatchList#######

class WatchList(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        paginator = WatchlistSetPagination()
        watchlist = Watchlist.objects.filter(is_delete=False)
        result_page = paginator.paginate_queryset(watchlist, request)
        serializer = WatchListSerializer(result_page, many=True)
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
    def post(self, request):
        serializer = WatchListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':200,
                             'message':'delete successfully'},status=status.HTTP_200_OK)
        return Response({'status':400,
                             'message':serializer.errors
                             },status=status.HTTP_400_BAD_REQUEST)
class WatchListUpdate(APIView):
    def get_object(self, pk):
        try:
            return Watchlist.objects.get(pk=pk)
        except Watchlist.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def get(self, request, pk):
        watchlist = self.get_object(pk)
        serializer = WatchListSerializer(watchlist)
        return Response({'status':200,
                             'message':'found successfully',
                             'data':serializer.data},status=status.HTTP_200_OK)


    def patch(self, request, pk):
        watchlist = self.get_object(pk)
        serializer = WatchListSerializer(watchlist, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':200,
                             'message':'update successfully'
                             },status=status.HTTP_200_OK)
        return Response({'status':400,
                             'message':'update fail'
                             },status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        watchlist = self.get_object(pk)
        serializer = WatchListSerializer(watchlist, 
            data =
            {
                'is_delete': True,
                
            }, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':200,
                             'message':'delete successfully'},status=status.HTTP_200_OK)
        return Response({'status':400,
                             'message':serializer.errors
                             },status=status.HTTP_400_BAD_REQUEST)

class DownloadFile(APIView):
    lookup_field = 'folder_id'
    def get(self, request, folder_id,format=None):
        rootPath="download/"
        folder=None
        zip_file_name=None
        try:
            folder = file = Folder.objects.get(pk=folder_id)
            if file.type=="File":
                file_path = file.files.path
                content_type, encoding = mimetypes.guess_type(file_path)
                content_type = content_type or 'application/octet-stream'
                response = HttpResponse(open(file_path, 'rb'), content_type=content_type)
                # Tạo response từ tệp tin
                response['Content-Disposition'] = f'attachment; filename="{file.files.name}"'
                print(file_path)
                # shutil.copy2(file_path, save_path)
                return response
            
            # downloadfolder
            folderList = Folder.objects.filter(path__startswith=folder.path)
            zip_file_name = f"{folder.name}.zip"
            # create folder
            for item in folderList:
                if item.type=='Folder': 
                    os.makedirs(os.path.join(rootPath,item.path), exist_ok=True)
            # create file
            for item in folderList:
                if item.type=='File': 
                    file_path = item.files.path
                    with open(file_path, 'rb') as source_file:
                        file_content = source_file.read()
                    with open(os.path.join(rootPath,item.path), 'wb') as new_file:
                        new_file.write(file_content)
            # create zip 
            with zipfile.ZipFile(os.path.join(rootPath, zip_file_name), 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(os.path.join(rootPath,folder.path)):
                    print(root)
                    for file in files:
                        abs_path = os.path.join(root, file)
                        rel_path = os.path.relpath(abs_path, os.path.join(rootPath,folder.path))
                        arcname = os.path.join(folder.name, rel_path)
                        zipf.write(abs_path, arcname=arcname)
                    for dir in dirs:
                        abs_path = os.path.join(root, dir)
                        rel_path = os.path.relpath(abs_path, os.path.join(rootPath,folder.path))
                        arcname = os.path.join(folder.name, rel_path)
                        zipf.write(abs_path, arcname=arcname)
            # return zip
            with open(os.path.join(rootPath,zip_file_name), 'rb') as zip_file:
                response = HttpResponse(zip_file.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{zip_file_name}"'
                return response
        except Folder.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
        finally:
            print('kdkd ')
            # shutil.rmtree(os.path.join(rootPath, folder.path))
            # os.remove(os.path.join(rootPath, zip_file_name))
        

class DownloadConvertAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer

    def retrieve(self, request, *args, **kwargs):
        portfolio = self.get_object()

        # Tạo DataFrame từ thông tin hồ sơ
        portfolio_data = {
            'title': portfolio.title,
            'identification_code': portfolio.identification_code,
            'classification': portfolio.classification,
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

                                                                                           
class Multi_portfolio_DownloadConvertAPIView(APIView):
    def get(self, request, ids, *args, **kwargs):
        # Chuyển đổi danh sách ID từ chuỗi thành danh sách các số nguyên
        try:
            id_list = [int(id) for id in ids.split(',')]
        except ValueError:
            return Response({"error": "Invalid ID format"}, status=status.HTTP_400_BAD_REQUEST)

        # Lấy danh sách các đối tượng Portfolio dựa trên danh sách ID
        portfolios = Portfolio.objects.filter(id__in=id_list)

        # Kiểm tra xem số lượng đối tượng lấy được có trùng khớp với số lượng ID đã truyền
        if len(portfolios) != len(id_list):
            return Response({"error": "Some portfolios do not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Tạo tệp tin zip và thêm các tệp tin Excel vào
        zip_file = BytesIO()
        with zipfile.ZipFile(zip_file, 'w') as zf:
            for portfolio in portfolios:
                portfolio_data = {
                    'title': portfolio.title,
                    'identification_code': portfolio.identification_code,
                    # Thêm các trường dữ liệu khác của Portfolio vào dictionary
                }
                portfolio_df = pd.DataFrame([portfolio_data])
                portfolio_excel_file = BytesIO()
                with pd.ExcelWriter(portfolio_excel_file, engine='openpyxl') as writer:
                    portfolio_df.to_excel(writer, index=False)
                portfolio_excel_file.seek(0)
                zf.writestr(f'portfolio_{portfolio.id}.xlsx', portfolio_excel_file.getvalue())

                # Thêm các tệp tin liên quan vào zip
                documents = Document.objects.filter(portfolio=portfolio)
                for document in documents:
                    file_path = os.path.join(settings.MEDIA_ROOT, str(document.files))
                    arcname = f'portfolio_{portfolio.id}/{os.path.basename(str(document.files))}'
                    zf.write(file_path, arcname=arcname)

        # Đặt tiêu đề và kiểu dữ liệu cho phản hồi
        response = HttpResponse(zip_file.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=data.zip'
        return response  
    
class BulkDeleteAPI(APIView):
    def delete(self, request, *args, **kwargs):
        portfolio_ids = request.data.get('portfolio_ids', [])
        warehouse_ids = request.data.get('warehouse_ids', [])
        document_ids = request.data.get('document_ids', [])
        folder_ids = request.data.get('folder_ids', [])
        success_count = 0
        
        # Soft delete portfolios and associated documents
        try:
            for portfolio_id in portfolio_ids:
                try:
                    portfolio = Portfolio.objects.get(id=int(portfolio_id))
                    portfolio.soft_delete(request)
                    document = Document.objects.get(portfolio=portfolio_id)
                    document.soft_delete(request)
                    success_count += 1
                    data = {
                            'status': '200',
                            'message':'Deleted successfully'
                    }
                except Portfolio.DoesNotExist:
                    data = {
                        'status': status.HTTP_404_NOT_FOUND,
                        'message': f'portfolio with ID {portfolio_id} not found'
                    }
                    return Response(data, status=status.HTTP_404_NOT_FOUND)
                except Document.DoesNotExist:
                    for portfolio_id in portfolio_ids:
                        portfolio = Portfolio.objects.get(id=int(portfolio_id))
                        portfolio.soft_delete(request)
                        success_count += 1
                    data = {
                        'status': '200',
                        'message':'Deleted successfully'
                    }
                    return Response(data, status=status.HTTP_200_OK)

        # Soft delete documents
            try:
                for document_id in document_ids:
                    document = Document.objects.get(id=int(document_id))
                    document.soft_delete(request)
                    success_count += 1
                    data = {
                            'status': '200',
                            'message':'Deleted successfully'
                        }
            except Document.DoesNotExist:
                data = {
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': f'Document with ID {document_id} not found'
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
                        
        # Soft delete warehouses
            try:
                for warehouse_id in warehouse_ids:
                    warehouse = Warehouse.objects.get(id=int(warehouse_id))
                    warehouse.soft_delete(request)

                    if warehouse.type_warehouse == ChoicesTypeWarehouse.Shelf.value:
                        # Get all boxcases related to the shelf
                        boxcases = Warehouse.objects.filter(parent_warehouse=warehouse)
                        for boxcase in boxcases:
                            boxcase.soft_delete(request)
                    
                    if warehouse.type_warehouse == ChoicesTypeWarehouse.Warehouse.value:
                        # Get all subwarehouses related to the warehouse
                        warehouse = Warehouse.objects.get(id=int(warehouse_id))
                        warehouse.soft_delete(request)
                        shelf = Warehouse.objects.get(parent_warehouse=warehouse)
                        shelf.soft_delete(request)
                        boxcases = Warehouse.objects.get(parent_warehouse=shelf)
                        boxcases.soft_delete(request)

                    success_count += 1
                    data = {
                            'status': '200',
                            'message':'Deleted successfully'
                        }
                # return Response(data, status=status.HTTP_200_OK)
            except Warehouse.DoesNotExist:
                data = {
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': f'Folder with ID {success_count} not found'
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
                        
        # Soft delete folders
            for folder_id in folder_ids:
                try:
                    folder =  Folder.objects.get(id=folder_id)
                    folders = Folder.objects.filter(path__startswith=folder.path)
                    for i in folders:
                        i.soft_delete(request)
                    data = {
                            'status': '200',
                            'message':'Deleted successfully'
                        }
                except:
                    data = {
                        'status': '500',
                        'message': 'không tìm thấy id'
                    }
                return Response(data, status=status.HTTP_200_OK)
        except:
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        

class UserFilter(filters.FilterSet):
    username = filters.CharFilter(field_name='username', lookup_expr='icontains')
    class Meta:
        model = User
        fields = ['username']
class UserListCreate(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = UserFilter
    paginator = CustomPagination()
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':201,
                             'message':'created successfully',
                             'data':serializer.data}, 
                             status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateDelete(APIView):
    permission_classes = [permissions.IsAdminUser]
    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except  User.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def get(self, request, pk):
        user = self.get_user(pk)
        serializer = UserSerializer(user)
        return Response({'status':201,
                        'message':'found',
                        'data':serializer.data},status=status.HTTP_302_FOUND)


    def patch(self, request, pk):
        user = self.get_user(pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':201,
                             'message':'created successfully',
                             'data':serializer.data},status=status.HTTP_200_OK)
        return Response({'status':400,
                        'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_user(pk)
        user.delete()
        return Response({'status': 204,
                         'message': 'deleted successfully'})