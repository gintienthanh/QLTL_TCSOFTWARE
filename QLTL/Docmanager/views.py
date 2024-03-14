import concurrent.futures
import datetime
import os
import re
import shutil
from django.conf import settings
from django.shortcuts import render
from Docmanager.permissions import Check_owner_factory, check_shared_group_factory, check_group_permisison_factory
from QLTL.settings import EXPORT_PATH_FILE
from .model_serializers import*
from .models import*
from rest_framework import authentication, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse, HttpResponse
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
import mimetypes
import pandas as pd
from io import BytesIO
import zipfile
from django.core.files.storage import default_storage
import django_filters
from django.utils import timezone
from django.db.models import F, Case, When, Value, CharField
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User,Permission,Group
# Create your views here.
class CustomPagination(PageNumberPagination):


    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 1000

    def get_page_size(self, request):
        limit = self.get_limit(request)
        return min(limit, self.max_limit)

    def get_limit(self, request):
        limit_param = request.GET.get(self.limit_query_param)
        if limit_param is None:
            return self.page_size

        try:
            limit = int(limit_param)
            if limit < 0:
                limit = self.page_size
        except ValueError:
            limit = self.page_size

        return limit

    def get_offset(self, request):
        offset_param = request.GET.get(self.offset_query_param)
        if offset_param is None:
            return 0

        try:
            offset = int(offset_param)
            if offset < 0:
                offset = 0
        except ValueError:
            offset = 0

        return offset

   

    def get_paginated_response(self, data):
        limit = self.get_limit(self.request)
        offset = self.get_offset(self.request)
        queryset = self.page.paginator.object_list

        total_count = self.page.paginator.count
        total_pages = self.page.paginator.num_pages
        current_page = self.page.number

       

        next_page = self.get_next_link()
        previous_page = self.get_previous_link()

        has_more = offset + limit < total_count

        return Response({
            "status": "200",
            "message": "Data found successfully",
            "pagination": {
                "count": total_count,
                "total_pages": total_pages,
                "current_page": current_page,
                "next_page": next_page,
                "previous_page": previous_page,
                "limit": limit,
                "offset": offset,
                "has_more": has_more,
            },
            "data": data
        })
# class PortfolioSetPagination(CustomPagination):
#     page_size = 12
#     page_size_query_param = 'page_size'
#     max_page_size = 1000  
    
# class FolderSetPagination(CustomPagination):
#     page_size = 12
#     page_size_query_param = 'page_size'
#     max_page_size = 1000   
# class WarehouseSetPagination(CustomPagination):
#     page_size = 1000
#     page_size_query_param = 'page_size'
#     max_page_size = 1000  
# class ShareSetPagination(CustomPagination):
#     page_size = 12
#     page_size_query_param = 'page_size'
#     max_page_size = 1000  

class WatchlistSetPagination(CustomPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000
# class DocumentSetPagination(CustomPagination):
#     page_size = 12
#     page_size_query_param = 'page_size'
#     max_page_size = 1000

#######PORTFOLIO######

class PortfolioFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    usage_policy = filters.CharFilter(field_name='usage_policy', lookup_expr='icontains')
    
    class Meta:
        model = Portfolio
        fields = ['title', 'usage_policy']
class PortfolioListCreate(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
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
    paginator = CustomPagination()
    
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
    permission_classes = [permissions.IsAuthenticated]
    def get_portfolio(self, pk):
        try:
            return Portfolio.objects.get(pk=pk)
        except Portfolio.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def get(self, request, pk):
        portfolio = self.get_portfolio(pk)
        serializer = PortfolioSerializer(portfolio)
        return Response({'status':201,
                        'message':'found',
                        'data':serializer.data},status=status.HTTP_302_FOUND)


    def patch(self, request, pk):
        portfolio = self.get_portfolio(pk)
        serializer = PortfolioSerializer(portfolio, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.validated_data['updated_at'] = timezone.now()
            serializer.validated_data['editor'] = request.user
            serializer.save()
            return Response({'status':201,
                             'message':'created successfully',
                             'data':serializer.data},status=status.HTTP_200_OK)
        return Response({'status':400,
                        'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        instance = Portfolio.objects.get(pk=pk)
        instance.soft_delete(request)
        document = Document.objects.get(portfolio=pk)
        document.soft_delete(request)
        
        serializers = PortfolioSerializer(instance)
        docserializers = DocumentSerializer(document)
        
        return Response({'status':200,
                             'message':'delete successfully',
                             'dataportfolio': serializers.data,
                             'datadocment': docserializers.data
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
    paginator = CustomPagination()
    
    def get_queryset(self):
        
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            queryset = queryset.filter(create_by=user, is_delete=False)
        return queryset 
    
    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['create_by'] = request.user   
            serializer.save()
            return Response({'status':201,
                             'message':'created successfully',
                             'data':serializer.data}, 
                             status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DocumentUpdateDelete(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_document(self, pk):
        try:
            return Document.objects.get(pk=pk)
        except  Document.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def get(self, request, pk):
        document = self.get_document(pk)
        serializer = DocumentSerializer(document)
        return Response({'status':201,
                        'message':'found',
                        'data':serializer.data},status=status.HTTP_302_FOUND)


    def patch(self, request, pk):
        document = self.get_document(pk)
        serializer = DocumentSerializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.validated_data['updated_at'] = timezone.now()
            serializer.validated_data['editor'] = request.user
            serializer.save()
            return Response({'status':201,
                             'message':'created successfully',
                             'data':serializer.data},status=status.HTTP_200_OK)
        return Response({'status':400,
                        'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        instance = Document.objects.get(pk=pk)
        instance.soft_delete(request)
        return Response({'status':200,
                             'message':'delete successfully'
                            })
        
        
########FOLDER#######

class FolderFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    
    
    class Meta:
        model = Folder
        fields = ['name', 'parent_folder', 'type']





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
    paginator = CustomPagination()
    
    def get_queryset(self):
        
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            queryset = queryset.filter(create_by=user, is_delete = False, parent_folder = None)
        return queryset 
    def extract_and_convert_to_integer(self,name,data):
        name_list = []
        for i in data:
            name_list.append(i['name'])
        for i in name_list:
            if name in name_list:
                match = re.search(r'\((\d+)\)$', name)
                if match:
                    number_str = match.group(1)
                    number = int(number_str)
                    number += 1
                    new_name = re.sub(r'\(\d+\)$', f'({number})', name)
                    name = new_name
        return name
    def post(self, request):
        serializer = FolderSerializer(data=request.data,partial=True)
        files = request.FILES.getlist('files')
        name = request.POST.get('name')
        parent_folder_id = request.POST.get('parent_folder')
        user = request.user
        if name:
            name = name.rstrip()
        else:
            name = request.data.get('name')
            if name:
                name = name.rstrip()
            else:
                name = None
        if not parent_folder_id:
            parent_folder_id = request.data.get('parent_folder')
        if serializer.is_valid():
            if parent_folder_id:
                parent_folder = Folder.objects.get(id=parent_folder_id)
                queryset = Folder.objects.filter(parent_folder = parent_folder)
                owner = parent_folder.owner
                path = parent_folder.path
            else:
                parent_folder = None
                path = ''
                queryset = Folder.objects.filter(parent_folder = None)
            serializer_db = FolderSerializer(queryset,many=True)
            data = serializer_db.data
            name_list = []
            for i in data:
                name_list.append(i['name'])
            if files:
                type = 'File'
                for file in files:
                    name = file.name
                    start_index = name.rfind('.')
                    name_default = name[:start_index] + "(1)" + name[start_index:]
                    if name not in name_list: 
                        newname = name
                    elif name_default not in name_list and name in name_list:
                        newname = name_default
                    elif name_default in name_list and name in name_list:
                        newname = self.extract_and_convert_to_integer(name_default,data)
                    serializer.save(type= type, files=file,file_size = file.size, path = path + newname, name = newname,parent_folder=parent_folder,create_by = user)
            else:
                type = 'Folder'
                name_default = name + " (1)"
                if name not in name_list: 
                    newname = name
                elif name_default not in name_list and name in name_list:
                    newname = name_default
                elif name_default in name_list and name in name_list:
                    newname = self.extract_and_convert_to_integer(name_default,data)
                serializer.save(type = type,file_size = 0,path = path + newname + "/",name = newname,parent_folder=parent_folder,create_by = user)
            response = {
                "status": "200",
                "message": "created successfully",
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response({'status':400}, status=status.HTTP_400_BAD_REQUEST)



class FolderUpdateDelete(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_folder(self, pk):
        try:
            return Folder.objects.get(pk=pk)
        except Folder.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def get(self, request, pk):
        folder = self.get_folder(pk)
        serializer = FolderSerializer(folder)
        return Response({'status':302,
                             'message':'found successfully',
                             'data':serializer.data},status=status.HTTP_302_FOUND)
    def patch(self, request, pk):
        folder = self.get_folder(pk)
        serializer = FolderSerializer(folder, data=request.data,partial=True)
        name = request.POST.get('name')
        user = request.user
        if name:
            name = name.rstrip()
        else:
            name = request.data.get('name')
            if name:
                name = name.rstrip()
            else:
                name = folder.name
        parent_folder_id = request.POST.get('parent_folder')
        if not parent_folder_id:
            parent_folder_id = request.data.get('parent_folder')
        if serializer.is_valid():
            if parent_folder_id:
                parent_folder = Folder.objects.get(id=parent_folder_id)
                queryset = Folder.objects.filter(parent_folder = parent_folder)
                path = parent_folder.path
            else:
                parent_folder = None
                path = '/'
                queryset = Folder.objects.filter(parent_folder = None)
            serializer_db = FolderSerializer(queryset,many=True)
            data = serializer_db.data
            name_list = []
            for i in data:
                name_list.append(i['name'])
            name_default = name + " (1)"
            if name not in name_list: 
                newname = name
            elif name_default not in name_list and name in name_list:
                newname = name_default
            elif name_default in name_list and name in name_list:
                newname = FolderListCreate.extract_and_convert_to_integer(name_default,data)
            serializer.save(path = path + newname + "/", name = newname,parent_folder=parent_folder,update_by = user)
            response = {
                "status":200,
                "message": "updated successfully",
                "data": {
                    "folder": serializer.data,  
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response({'status':400}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk):
            folder = self.get_object(pk)
            try:
                folders = Folder.objects.filter(path__startswith=folder.path)
                for i in folders:
                    i.soft_delete(request)
                return Response({'status':200,
                                'message':'delete successfully'
                                }, status=status.HTTP_200_OK)
            except:
                return Response({'status':400}, status=status.HTTP_400_BAD_REQUEST)



class ShareFilter(filters.FilterSet):
    class Meta:
        model = Share
        fields = ['owner','create_by','document','folder']
   
class APIShareListCreate(generics.ListCreateAPIView):
    queryset = Share.objects.all()
    serializer_class = ShareSerializer
    filter_backends = [filters.DjangoFilterBackend]
    

    filterset_class = ShareFilter
    paginator = CustomPagination()
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), check_group_permisison_factory('share')(self)]
        elif self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            queryset = queryset.filter(create_by=user, is_delete=False)
        return queryset
    
    def post(self, request):
        try:
            serializer = ShareSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                share = Share.objects.get(
                    folder=serializer.validated_data.get('folder'),
                    document=serializer.validated_data.get('document'),
                    create_by=request.user,
                    owner=serializer.validated_data.get('owner'),
                    type=serializer.validated_data.get('type')
                    )
                serializer = ShareSerializer(share)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Share.DoesNotExist:
            serializer.save(create_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({"error": "Có lỗi xảy ra"}, status=status.HTTP_400_BAD_REQUEST)
        
class APIShareUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [check_shared_group_factory(Share(),'edit') | Check_owner_factory(Share())]
    queryset = Share.objects.all()
    serializer_class = ShareSerializer
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.updated_at = timezone.now()
        instance.editor = request.user
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'status':200, 'message':'updated successfully'},serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete=True
        instance.delete_at=timezone.now() 
        instance.delete_by=request.user
        self.perform_update(instance)
        return Response({'status':200,'message':'destroyed'},status=status.HTTP_204_NO_CONTENT)  

class PermissionFilter(filters.FilterSet):
    class Meta:
        model = Permission
        fields = ['name']
class APIPermissionListCreate(generics.ListCreateAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = PermissionFilter
    paginator = CustomPagination()
    # def get_permissions(self):
    #     if self.request.method == 'POST':
    #         return [permissions.IsAuthenticated()]
    #     elif self.request.method == 'GET':
    #         return [permissions.IsAuthenticated()]
    #     return super().get_permissions()
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            queryset = queryset.filter( is_delete=False)
        return queryset
    
    
class APIPermissionUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [check_shared_group_factory(Share(),'edit') | Check_owner_factory(Share())]
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.updated_at = timezone.now()
        instance.editor = request.user
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'status':400,'message':'Yêu cầu không hợp lệ hoặc thiếu thông tin cần thiết'},status=status.HTTP_400_BAD_REQUEST)  
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete=True
        instance.delete_at=timezone.now() 
        instance.delete_by=request.user
        self.perform_update(instance)
        return Response({'status':200,'message':'destroyed'},status=status.HTTP_204_NO_CONTENT)  

class GroupFilter(filters.FilterSet):
    class Meta:
        model = Group
        fields = ['name']
class APIGroupListCreate(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = GroupFilter
    paginator = CustomPagination()
    # def get_permissions(self):
    #     if self.request.method == 'POST':
    #         return [permissions.IsAuthenticated()]
    #     elif self.request.method == 'GET':
    #         return [permissions.IsAuthenticated()]
    #     return super().get_permissions()
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            queryset = queryset.filter( is_delete=False)
        return queryset
    
    
class APIGroupUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [check_shared_group_factory(Share(),'edit') | Check_owner_factory(Share())]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.updated_at = timezone.now()
        instance.editor = request.user
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'status':400,'message':'Yêu cầu không hợp lệ hoặc thiếu thông tin cần thiết'},status=status.HTTP_400_BAD_REQUEST)  
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete=True
        instance.delete_at=timezone.now() 
        instance.delete_by=request.user
        self.perform_update(instance)
        return Response({'status':200,'message':'destroyed'},status=status.HTTP_204_NO_CONTENT)  

    

class GroupUserView(APIView):
   
    def get(self, request, pk):
        groups = Group.objects.filter(user = request.user)
        serializer = GroupSerializer(groups,many=True)
        return Response(serializer.data)

    def put(seft, request,pk):
        group_id = pk
        user_ids = request.data.get('user_ids', '')
        user_ids_list = [int(user_id) for user_id in user_ids.split(',') if user_id.isdigit()]

        try:
            group = Group.objects.get(id=group_id)
            users = User.objects.filter(id__in=user_ids_list)
            # Lấy danh sách người dùng đã tồn tại trong nhóm
            existing_users = group.user_set.all()
            # Xóa các người dùng đã tồn tại trong nhóm nhưng không có trong danh sách thêm
            users_to_remove = existing_users.exclude(id__in=user_ids_list)
            for user in users_to_remove:
                user.groups.remove(group)
            # Thêm các người dùng từ danh sách thêm
            for user in users:
                user.groups.add(group)
            return Response({'message': 'update group successfully.'},status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class GroupPermissionView(APIView):
    def get(self, request, pk):
        group_id = pk
        permissions = Permission.objects.filter(group=group_id)
        print(permissions)

        serializer = PermissionSerializer(permissions,many=True)
        return Response(serializer.data)
        
    # def post(self, request, pk):
    #     group_id = pk
    #     user_ids = request.query_params.get('user_ids', '')
    #     user_ids_list = [int(user_id) for user_id in user_ids.split(',') if user_id.isdigit()]
        

    #     try:
    #         group = Group.objects.get(id=group_id)
    #         users = User.objects.filter(id__in=user_ids_list)
    #         for user in users:
    #             user.groups.add(group)
    #         return Response({'message': 'Users added to group successfully.'}, status=status.HTTP_200_OK)

    #     except Group.DoesNotExist:
    #         return Response({'error': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
    def put(seft, request,pk):
        group_id = pk
        permission_ids = request.data.get('permission_ids', '')
        permission_ids_list = [int(permission_id) for permission_id in permission_ids.split(',') if permission_id.isdigit()]
        print(permission_ids_list)

        try:
            group = Group.objects.get(id=group_id)
            permissions = Permission.objects.filter(id__in=permission_ids_list)
            # Lấy danh sách permission đã tồn tại trong nhóm
            existing_permissions = group.permissions.all()
            # Xóa các permission đã tồn tại trong nhóm nhưng không có trong danh sách thêm
            permissions_to_remove = existing_permissions.exclude(id__in=permission_ids_list)
            for permission in permissions_to_remove:
                group.permissions.remove(permission)
            
            # Thêm các permission từ danh sách thêm
            for permission in permissions:
                group.permissions.add(permission)
            return Response({'message': 'update group successfully.'},status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
class UserPermissionView(APIView):
    def get(self, request, pk):
        user_id = pk
        permissions = Permission.objects.filter(user=user_id)
        print(permissions)

        serializer = PermissionSerializer(permissions,many=True)
        return Response(serializer.data)
        
    # def post(self, request, pk):
    #     group_id = pk
    #     user_ids = request.query_params.get('user_ids', '')
    #     user_ids_list = [int(user_id) for user_id in user_ids.split(',') if user_id.isdigit()]
        

    #     try:
    #         group = Group.objects.get(id=group_id)
    #         users = User.objects.filter(id__in=user_ids_list)
    #         for user in users:
    #             user.groups.add(group)
    #         return Response({'message': 'Users added to group successfully.'}, status=status.HTTP_200_OK)

    #     except Group.DoesNotExist:
    #         return Response({'error': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
    def put(seft, request,pk):
        user_id = pk
        permission_ids = request.data.get('permission_ids', '')
        permission_ids_list = [int(permission_id) for permission_id in permission_ids.split(',') if permission_id.isdigit()]
        print(permission_ids_list)

        try:
            user = User.objects.get(id=user_id)
            permissions = Permission.objects.filter(id__in=permission_ids_list)
            # Lấy danh sách permission đã tồn tại trong user
            existing_permissions = user.user_permissions.all()
            # Xóa các permission đã tồn tại trong user nhưng không có trong danh sách thêm
            permissions_to_remove = existing_permissions.exclude(id__in=permission_ids_list)
            for permission in permissions_to_remove:
                user.user_permissions.remove(permission)
            
            # Thêm các permission từ danh sách thêm
            for permission in permissions:
                user.user_permissions.add(permission)
            return Response({'message': 'update user successfully.'},status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        


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
    paginator = CustomPagination()
    
    def get_queryset(self):
        
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            queryset = queryset.filter(create_by=user, is_delete = False)
        return queryset 
        
    def post(self, request):
        try:
            serializer = WarehouseSerializer(data=request.data)
            id = request.data.get('parent_warehouse_id')
            if serializer.is_valid():
                 
                parent_warehouse =Warehouse.objects.get(id=id)    
                serializer.save(parent_warehouse=parent_warehouse, create_by=request.user)
    
                return Response({'status':201,
                                'message':'created successfully',
                                'data':serializer.data},status=status.HTTP_201_CREATED)
            return Response({'status':400,
                            'message':'created fail'},status=status.HTTP_400_BAD_REQUEST)
        except Warehouse.DoesNotExist:
            serializer.save(create_by=request.user)
            return Response({'status':201,
                            'message':'created successfully',
                            'data':serializer.data},status=status.HTTP_201_CREATED)
    
        
        except Exception as e:
            return Response({'status':400,
                            'message':'created fail'},status=status.HTTP_400_BAD_REQUEST)
            
            
            
######WAREHOUSE#######


class WarehouseUpdateDelete(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def get_warehouse(self, pk):
        try:
            return Warehouse.objects.get(pk=pk)
        except Warehouse.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def get(self, request, pk):
        warehouse = self.get_warehouse(pk)
        serializer = WarehouseSerializer(warehouse)
        return Response({'status':200,
                             'message':'found successfully',
                             'data':serializer.data},status=status.HTTP_200_OK)


    def patch(self, request, pk):
        warehouse = self.get_warehouse(pk)
    
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
        warehouse = self.get_warehouse(pk)
        try:
            delete_success = warehouse.soft_delete(request)

            if warehouse.type_warehouse == ChoicesTypeWarehouse.Shelf.value:
                # Lấy tất cả boxcase liên quan đến shelf
                boxcases = Warehouse.objects.filter(parent_warehouse=warehouse)
                for boxcase in boxcases:
                    if  boxcase.soft_delete(request):
                        return Response({"message": "Xóa thành công"}, status=status.HTTP_200_OK)
            elif warehouse.type_warehouse == ChoicesTypeWarehouse.BoxCase.value:
                # Lấy shelf liên quan đến boxcase
                shelf = warehouse.parent_warehouse
                if  shelf.soft_delete(request):
                    return Response({"message": "Xóa thành công"}, status=status.HTTP_200_OK)
            else:
                # Lấy tất cả warehouse con liên quan đến warehouse
                subwarehouses = warehouse.subwarehouse.all()
                for subwarehouse in subwarehouses:
                    if  subwarehouse.soft_delete(request):
                        return Response({"message": "Xóa thành công"}, status=status.HTTP_200_OK)
            
            return Response({'status': 200, 'message': 'Xóa thành công'}, status=status.HTTP_200_OK)
        
        except:
            return Response({'status': 400}, status=status.HTTP_400_BAD_REQUEST)


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

######DOWNLOAD#######

class DownloadFile(APIView):
    lookup_field = 'folder_id'
    def get(self, request, folder_id,format=None):
        folder=None
        zip_file_name=None
        set_file_fail = set()
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
                    os.makedirs(os.path.join(EXPORT_PATH_FILE,item.path), exist_ok=True)
            # create file 
            def write_file(item):    
                if item.type=='File':
                    file_path = item.files.path
                    if not os.path.exists(file_path):
                        set_file_fail.add(file_path)
                        return
                    with open(file_path, 'rb') as source_file:
                            file_content = source_file.read()
                    with open(os.path.join(EXPORT_PATH_FILE,item.path), 'wb') as new_file:
                        new_file.write(file_content)
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    futures = []
                    for obj in folderList:
                        future = executor.submit(write_file, obj)
                        futures.append(future)
            # create zip 
            with zipfile.ZipFile(os.path.join(EXPORT_PATH_FILE, zip_file_name), 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(os.path.join(EXPORT_PATH_FILE,folder.path)):
                    for file in files:
                        abs_path = os.path.join(root, file)
                        rel_path = os.path.relpath(abs_path, os.path.join(EXPORT_PATH_FILE,folder.path))
                        arcname = os.path.join(folder.name, rel_path)
                        zipf.write(abs_path, arcname=arcname)
                    for dir in dirs:
                        abs_path = os.path.join(root, dir)
                        rel_path = os.path.relpath(abs_path, os.path.join(EXPORT_PATH_FILE,folder.path))
                        arcname = os.path.join(folder.name, rel_path)
                        zipf.write(abs_path, arcname=arcname)
            # return zip
            with open(os.path.join(EXPORT_PATH_FILE,zip_file_name), 'rb') as zip_file:
                response = HttpResponse(zip_file.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{zip_file_name}"'
                return response
        except Folder.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
        finally:
            if os.path.exists(os.path.join(EXPORT_PATH_FILE, folder.path)):
                shutil.rmtree(os.path.join(EXPORT_PATH_FILE, folder.path))  
            # os.remove(os.path.join(rootPath, zip_file_name))
            for e in set_file_fail:
                print(e)
        

                                                                                           
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
        for portfolio_id in portfolio_ids:
            try:
                portfolio = Portfolio.objects.get(id=int(portfolio_id))
                portfolio.soft_delete(request)
                documents = Document.objects.filter(portfolio=portfolio)
                documents.update(is_delete=True, delete_at=timezone.now())
                success_count += 1
            except Portfolio.DoesNotExist:
                data = {
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': f'portfolio with ID {portfolio_id} not found'
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)

        # Soft delete documents
        for document_id in document_ids:
            try:
                document = Document.objects.get(id=int(document_id))
                document.soft_delete(request)
                success_count += 1
            except Document.DoesNotExist:
                data = {
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': f'Document with ID {document_id} not found'
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
                    
        # Soft delete warehouses
        for warehouse_id in warehouse_ids:
            try:
                warehouse = Warehouse.objects.get(id=int(warehouse_id))
                warehouse.soft_delete(request)

                if warehouse.type_warehouse == ChoicesTypeWarehouse.Shelf.value:
                    # Get all boxcases related to the shelf
                    boxcases = Warehouse.objects.filter(parent_warehouse=warehouse)
                    for boxcase in boxcases:
                        boxcase.soft_delete(request)
                elif warehouse.type_warehouse == ChoicesTypeWarehouse.BoxCase.value:
                    # Get the shelf related to the boxcase
                    shelf = warehouse.parent_warehouse
                    shelf.soft_delete(request)
                else:
                    # Get all subwarehouses related to the warehouse
                    subwarehouses = warehouse.subwarehouse.all()
                    for subwarehouse in subwarehouses:
                        subwarehouse.soft_delete(request)

                success_count += 1
            except Warehouse.DoesNotExist:
                data = {
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': f'Folder with ID {folder_id} not found'
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
                    
        # Soft delete folders
        for folder_id in folder_ids:
            try:
                folder = Folder.objects.get(id=folder_id)
                folders = Folder.objects.filter(path__startswith=folder.path)
                for i in folders:
                    i.soft_delete(request)
                success_count += 1
            except Folder.DoesNotExist:
                data = {
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': f'Folder with ID {folder_id} not found'
                }
                return Response(data, status=status.HTTP_404_NOT_FOUND)
        
        if success_count > 0:
            data = {
                'status': status.HTTP_200_OK,
                'message': f'Deleted {success_count} items successfully'
            }
            return Response(data, status=status.HTTP_200_OK)
        
        if success_count == 0:
                    data = {
                        'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                        'message': 'Failed to delete items'
                    }
                    return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


######USER#####                
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
           
