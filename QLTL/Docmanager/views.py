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
from django.http import FileResponse, Http404, HttpResponse
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
from rest_framework.permissions import IsAdminUser

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
            if limit <= 0:
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

#######PORTFOLIO######


class PortfolioListCreate(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    paginator = CustomPagination()
    
    
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            title_query = self.request.GET.get('title', None)   
            queryset = queryset.filter(create_by=user, is_delete=False)
            if title_query:
                queryset = queryset.filter(title__icontains=title_query)   
            queryset = queryset.order_by(F('updated_at').desc())
            
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


    

class DocumentListCreate(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    paginator = CustomPagination()
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            name_query = self.request.GET.get('name', None)
            portfolio_query = self.request.GET.get('portfolio_id', None)
            queryset = queryset.filter(create_by=user, is_delete=False)
            if name_query:
                queryset = queryset.filter(title__icontains=name_query)   
            if portfolio_query:
                queryset = queryset.filter(title__icontains=portfolio_query)   
            queryset = queryset.order_by(F('updated_at').desc())
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
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer  
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = FolderFilter
    paginator = CustomPagination()
    
    def get_queryset(self):
        
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            parent_folder = self.request.GET.get('parent_folder')
            if parent_folder:
                queryset = queryset.filter(create_by=user, is_delete = False, parent_folder = parent_folder)
            else:
                queryset = queryset.filter(create_by=user, is_delete = False, parent_folder = None)
            queryset = queryset.order_by(F('updated_at').desc())
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
                    file_size = file.size
                    start_index = name.rfind('.')
                    name_default = name[:start_index] + " (1)" + name[start_index:]
                    if name not in name_list: 
                        newname = name
                    elif name in name_list:
                        newname = self.extract_and_convert_to_integer(name_default,name_list)
                    newrecord = Folder(type= type, files=file,file_size = file_size, path = path + newname, name = newname,parent_folder=parent_folder,create_by = user,owner=owner)
                    newrecord.save()
                response = {
                    "status": 200,
                    "message": "created successfully",
                }
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
    permission_classes = [permissions.IsAuthenticated]
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
        old_path = folder.path
        parent_folder_id_old = folder.parent_folder_id
        if parent_folder_id_old:
            parent_old = Folder.objects.get(id = parent_folder_id_old)
            parent_name_old = parent_old.name
        else:
            parent_name_old = ''
        parent_folder_id = request.data.get('parent_folder')
        if serializer.is_valid():
            if parent_folder_id:
                parent_folder = Folder.objects.get(id=parent_folder_id)
                path = parent_folder.path
                parent_name = parent_folder.name
            else:
                parent_folder_id = folder.parent_folder
                parent_folder = None
                path = ''
                parent_name = ''
            if folder.type == "Folder":
                path = path + folder.name + "/"
            else:
                path = path + folder.name
            child_fol = Folder.objects.filter(path__startswith = old_path)
            for i in child_fol:
                path_child = self.change(i.path,parent_name_old,parent_name)
                i.path = path_child
                i.save()
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
        fields = ['owner', 'create_by', 'document', 'folder']
class APIShareListCreate(generics.ListCreateAPIView):
    serializer_class = ShareSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ShareFilter
    paginator = CustomPagination()
    # permission_classes = [check_group_permisison_factory('share')]
    # def get_permissions(self):
    #     if self.request.method == 'POST':
    #         return [permissions.IsAuthenticated(), ]
    #     elif self.request.method == 'GET':
    #         return [permissions.IsAuthenticated()]
    #     return super().get_permissions()
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated: 
            queryset = Share.objects.all().filter(create_by=user, is_delete=False)
            return queryset
        if user.is_superuser:
            queryset = Share.objects.all().get_queryset()
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
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
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
            queryset = queryset.filter()
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
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
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
            queryset = queryset.filter()
        return queryset
    def post(self, request):
        try:
            group_name = request.data.get('name','')
            if group_name is None:
                return Response({'status':404,
                                'message':"Group name is not valid."},status=status.HTTP_400_BAD_REQUEST)
            group = GroupSerializer(data = {'name':group_name}) 
            group.is_valid(raise_exception = True)
            group = group.save()

            permission_ids = request.data.get('permission_ids', '')
            permission_ids_list = [int(permission_id) for permission_id in permission_ids.split(',') if permission_id.isdigit()]
            permissions = Permission.objects.filter(id__in=permission_ids_list)
            # Thêm các permission từ danh sách thêm
            for permission in permissions:
                group.permissions.add(permission)
            return Response({'status':200,
                             'message':'created successfully'
                             },status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({'status':404,'error': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)
        except serializers.ValidationError as e:
            return Response({'status':400,"error": "Group name is exist"}, status=status.HTTP_400_BAD_REQUEST)   
    
    
class APIGroupUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = [check_shared_group_factory(Share(),'edit') | Check_owner_factory(Share())]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            group_name = request.data.get('name','')
            if group_name is None:
                return Response({'status':404,
                                'message':"Group name is not valid."},status=status.HTTP_400_BAD_REQUEST)
            instance.name = group_name
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception = True)
            self.perform_update(serializer)
            # instance.save()
            permission_ids = request.data.get('permission_ids', '')
            permission_ids_list = [int(permission_id) for permission_id in permission_ids.split(',') if permission_id.isdigit()]
            permissions = Permission.objects.filter(id__in=permission_ids_list)
            # Lấy danh sách permission đã tồn tại trong nhóm
            instance.permissions.clear()
            # Thêm các permission từ danh sách thêm
            for permission in permissions:
                instance.permissions.add(permission)
            return Response({'status':200,
                             'message':'update successfully'
                             },status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({'status':404,'error': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)
        except serializers.ValidationError as e:
            return Response({'status':400,"error": "Group name is exist"}, status=status.HTTP_400_BAD_REQUEST) 

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
        queryset = Permission.objects.filter(group=pk).order_by('content_type')
        filterset = PermissionFilter(request.GET, queryset=queryset)
        # Kiểm tra xem FilterSet có hợp lệ không 
        if filterset.is_valid():
            queryset = filterset.qs
        else:
            return Response(filterset.errors, status=400)
        serializer = PermissionSerializer(queryset, many=True)
        return Response({'status':200,
                        'message':'Data found successfully',
                        'data':serializer.data}, status=status.HTTP_200_OK)
class PermissionNotIncludedInGroup(APIView):
    def get(self, request, pk):
        permissions = Permission.objects.filter(group=pk)
        permission_without_in_group = Permission.objects.exclude(id__in = permissions).order_by('content_type')

        serializer = PermissionSerializer(permission_without_in_group,many=True)
        return Response({'status':200,
                        'message':'Data found successfully',
                        'data':serializer.data},status=status.HTTP_200_OK)
    
        
class UserPermissionView(APIView):
    def get(self, request, pk):
        user_id = pk
        permissions = Permission.objects.filter(user=user_id)
        print(permissions)

        serializer = PermissionSerializer(permissions,many=True)
        return Response(serializer.data)
        
    
   
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
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer 
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = WarehouseFilter
    paginator = CustomPagination()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            queryset = queryset.filter(create_by=user, is_delete = False)
        queryset = queryset.order_by(F('updated_at').desc())
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
                  

class WarehouseUpdateDelete(APIView):
    permission_classes = [permissions.IsAuthenticated]
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
                    boxcase.soft_delete(request)
                
            if warehouse.type_warehouse == ChoicesTypeWarehouse.Warehouse.value:
                # Lấy tất cả warehouse con liên quan đến warehouse
                subwarehouses = warehouse.subwarehouse.all()
                for subwarehouse in subwarehouses:
                    subwarehouse.soft_delete(request)
                    
                    # Xóa tất cả shelf liên quan đến warehouse con
                    shelves = Warehouse.objects.filter(parent_warehouse=subwarehouse)
                    for shelf in shelves:
                        shelf.soft_delete(request)
                        
                        # Lấy tất cả boxcase liên quan đến shelf
                        boxcases = Warehouse.objects.filter(parent_warehouse=shelf)
                        for boxcase in boxcases:
                            boxcase.soft_delete(request)
                            

                    
            return Response({'status': 200, 'message': 'Xóa thành công'}, status=status.HTTP_200_OK)
        
        except Warehouse.DoesNotExist:
            data = {
                'status': status.HTTP_404_NOT_FOUND,
                'message': f'Warehouse with ID {pk} not found'
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)
class WarehouseWithShelvesList(generics.ListAPIView):
    serializer_class = WarehouseSimpleSerializer
    paginator = CustomPagination()
    def get_queryset(self):
        # Lọc các kho có type_warehouse là "shelf" và parent_warehouse_id là NULL
        queryset = Warehouse.objects.filter(type_warehouse="shelf", parent_warehouse_id__isnull=False)
        
        # Lấy danh sách các parent_warehouse_id của các kho shelf
        shelf_parent_ids = queryset.values_list('parent_warehouse_id', flat=True)
        
        # Lấy thông tin của các kho cha tương ứng với parent_warehouse_id và in ra id kèm theo tên
        parent_warehouses = Warehouse.objects.filter(id__in=shelf_parent_ids)

        for warehouse in parent_warehouses:
            print(f"ID: {warehouse.id}, Name: {warehouse.name}")

        return parent_warehouses


class AllWarehouseAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    queryset = Warehouse.objects.filter(parent_warehouse__isnull=True)
    serializer_class = AllWarehouseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = WarehouseFilter
    pagination_class = CustomPagination
    

#######WatchList#######
class WatchlistFilter(filters.FilterSet):

    class Meta:
        model = Watchlist
        fields = ['document_id', 'folder_id']
class WatchListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Watchlist.objects.annotate(
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
    serializer_class = WatchListSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = WatchlistFilter
    paginator = CustomPagination
    
    def get_queryset(self):
        
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            queryset = queryset.filter(create_by=user, is_delete=False)
        return queryset 
    
    def post(self, request):
        serializer = WatchListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['create_by'] = request.user   
            serializer.save()
            return Response({'status':201,
                             'message':'created successfully',
                             'data':serializer.data}, 
                             status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class WatchListUpdateDelete(APIView):
    def get_watchlist(self, pk):
        try:
            return Watchlist.objects.get(pk=pk)
        except Watchlist.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def get(self, request, pk):
        watchlist = self.get_watchlist(pk)
        serializer = WatchListSerializer(watchlist)
        return Response({'status':200,
                             'message':'found successfully',
                             'data':serializer.data},status=status.HTTP_200_OK)


    def patch(self, request, pk):
        watchlist = self.get_watchlist(pk)
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
        watchlist = self.get_watchlist(pk)
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
       


######USER#####   
             
class UserFilter(filters.FilterSet):
    username = filters.CharFilter(field_name='username', lookup_expr='icontains')
    # email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    class Meta:
        model = User
        fields = ['username','email']
class APIUserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = UserFilter 
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).values('id','username', 'email')
        response_data = {
            "status":200,
            "message": "Success",
            "data": list(queryset)
        }
        if not queryset:
            response_data = {
                "status":200,
                "message": "User doesn't exist",
                "data": list(queryset)
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        return Response(response_data, status=status.HTTP_200_OK)
    
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
        try:
            user = self.get_user(pk)
            permission_ids = request.data.get('permissions')
            is_active = request.data.get('is_active')
            serializer = UserSerializer(user, data=request.data, partial=True)
            if not permission_ids:
                user.user_permissions.clear()
            for permission_id in permission_ids:
                    permission = Permission.objects.get(id=permission_id)
                    user.user_permissions.add(permission)
            user.is_active = is_active
            user.save()
            if serializer.is_valid():
                serializer.save()
                return Response({'status':201,
                                'message':'update successfully'
                                },status=status.HTTP_200_OK)
        except:
            return Response({'status':400,
                        'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_user(pk)
        user.delete()
        return Response({'status': 204,
                         'message': 'deleted successfully'})
   
class UserListApiView(generics.ListAPIView):
    serializer_class = UserSerializer 
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    
   
    def get(self, request, *args, **kwargs):
        queryset = User.objects.all().prefetch_related('groups', 'user_permissions', 'userprofile') 
        page = self.paginate_queryset(queryset)
       
        
        serialized_data = []
        
        if page is not None:
            for user in page:
                try:
                    user_profile = UserProfile.objects.get(user=user)
                    if user_profile.organization:
                        organization_data = {
                            'id': user_profile.organization.id,
                            'name': user_profile.organization.name,
                        }
                    else:
                        organization_data = None
                    user_profile_data = {
                        'phone': user_profile.phone,
                        'organization': organization_data
                    }
                except UserProfile.DoesNotExist:
                    user_profile_data = {}
                
                group_data = [{'id': group.id, 'name': group.name} for group in user.groups.all()]
                permission_data = [{'id': permission.id, 'name': permission.name} for permission in user.user_permissions.all()]
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'user_profile': user_profile_data,  
                    'is_active': user.is_active,
                    'groups': group_data,  
                    'user_permissions': permission_data, 
                }
                serialized_data.append(user_data)

            return self.get_paginated_response(serialized_data)

        
class RetentionPeriodListCreate(generics.ListCreateAPIView): 
    permission_classes = [permissions.IsAuthenticated] 
    queryset = RetentionPeriod.objects.all() 
    serializer_class = RetentionPeriodSerializer 
    paginator = CustomPagination() 
     
     
    def get_queryset(self): 
        queryset = super().get_queryset() 
        user = self.request.user 
         
        if user.is_authenticated:  # Check if user is authenticated 
            name_query = self.request.GET.get('name', None)   
             
            queryset = queryset.filter(create_by=user, is_delete=False) 
             
            if name_query: 
                queryset = queryset.filter(name__icontains=name_query) 
                 
            queryset = queryset.order_by(F('updated_at').desc()) 
             
        return queryset   
     
    def post(self, request): 
         
        serializer = RetentionPeriodSerializer(data=request.data) 
        if serializer.is_valid(): 
            serializer.validated_data['create_by'] = request.user    
            serializer.validated_data['owner'] = request.user 
            serializer.save() 
            return Response({'status':201, 
                             'message':'created successfully', 
                             'data':serializer.data},  
                             status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
    
class RetentionPeriodUpdateDelete(generics.RetrieveUpdateDestroyAPIView): 
    permission_classes = [permissions.IsAuthenticated] 
    def get_object(self, pk): 
        try: 
            return RetentionPeriod.objects.get(pk=pk) 
        except RetentionPeriod.DoesNotExist: 
            raise Http404("RetentionPeriod not found") 
    def get(self, request, pk): 
        retentionperiod = self.get_object(pk) 
        serializer = RetentionPeriodSerializer(retentionperiod) 
        return Response({'status':201, 
                        'message':'found', 
                        'data':serializer.data},status=status.HTTP_302_FOUND) 
 
 
    def patch(self, request, pk): 
        retentionperiod = self.get_object(pk) 
        serializer = RetentionPeriodSerializer(retentionperiod, data=request.data, partial=True) 
        if serializer.is_valid(): 
            serializer.validated_data['updated_at'] = timezone.now() 
            serializer.validated_data['editor'] = request.user    
 
             
            serializer.save() 
            return Response({'status':201, 
                             'message':'updated successfully', 
                             'data':serializer.data},status=status.HTTP_200_OK) 
        return Response({'status':400, 
                        'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST) 
 
    def delete(self, request, pk): 
        retentionperiod  = RetentionPeriod.objects.get(pk=pk)  
        retentionperiod.soft_delete(request)  # Xóa bảng Portfolio 
        serializer = RetentionPeriodSerializer(retentionperiod) 
 
        return Response({ 
                'status': 200, 
                'message': 'delete successfully', 
                'dataport': serializer.data, 
        }) 
         
         
 
 
class LanguageListCreate(generics.ListCreateAPIView): 
    permission_classes = [permissions.IsAuthenticated]
    queryset = Language.objects.all() 
    serializer_class = LanguageSerializer 
    paginator = CustomPagination() 
     
     
    def get_queryset(self): 
        queryset = super().get_queryset() 
        user = self.request.user 
         
        if user.is_authenticated:  # Check if user is authenticated 
            name_query = self.request.GET.get('name', None)   
            queryset = queryset.filter(create_by=user, is_delete=False) 
             
            if name_query: 
                queryset = queryset.filter(name__icontains=name_query) 
                 
            queryset = queryset.order_by(F('updated_at').desc()) 
             
        return queryset    
     
    def post(self, request): 
         
        serializer = LanguageSerializer(data=request.data) 
        if serializer.is_valid(): 
            serializer.validated_data['create_by'] = request.user    
            serializer.validated_data['owner'] = request.user 
            serializer.save() 
            return Response({'status':201, 
                             'message':'created successfully', 
                             'data':serializer.data},  
                             status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
   
  
    
    
    
class LanguageUpdateDelete(generics.RetrieveUpdateDestroyAPIView): 
    permission_classes = [permissions.IsAuthenticated] 
    def get_object(self, pk): 
        try: 
            return Language.objects.get(pk=pk) 
        except Language.DoesNotExist: 
            raise Http404("Language not found") 
    def get(self, request, pk): 
        language = self.get_object(pk) 
        serializer = LanguageSerializer(language) 
        return Response({'status':201, 
                        'message':'found', 
                        'data':serializer.data},status=status.HTTP_302_FOUND) 
 
    def patch(self, request, pk): 
        language = self.get_object(pk) 
        serializer = LanguageSerializer(language, data=request.data, partial=True) 
        if serializer.is_valid(): 
            serializer.validated_data['updated_at'] = timezone.now() 
            serializer.validated_data['editor'] = request.user    
 
             
            serializer.save() 
            return Response({'status':201, 
                             'message':'updated successfully', 
                             'data':serializer.data},status=status.HTTP_200_OK) 
        return Response({'status':400, 
                        'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST) 
 
 
 
 
    def delete(self, request, pk): 
        language  = Language.objects.get(pk=pk)  
        language.soft_delete(request)  
        serializer = LanguageSerializer(language) 
 
        return Response({ 
                'status': 200, 
                'message': 'delete successfully', 
                'dataport': serializer.data, 
        })
