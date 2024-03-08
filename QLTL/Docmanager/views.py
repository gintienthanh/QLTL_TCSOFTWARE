import concurrent.futures
import datetime
import os
import shutil
from django.conf import settings
from django.shortcuts import render
from Docmanager.permissions import CheckOwnerFactory, CheckSharedGroupdFactory
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

        

        next_page = self.get_next_link()
        previous_page = self.get_previous_link()
        total_pages = self.page.paginator.num_pages
        current_page = self.page.number
        total_count = self.page.paginator.count
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
            },
            "data": data,
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
        
class PortfolioBulkDelete (APIView):
    def delete(self, request, *args, **kwargs):
        portfolio_ids = request.data.get('portfolio_ids', [])
        success_count = 0
        
        for portfolio_id in portfolio_ids:
            try:
                portfolio = Portfolio.objects.get(id=int(portfolio_id))
                serializer = PortfolioSerializer(portfolio, 
                    data={
                        'is_delete': True,
                    }, partial=True)
                if serializer.is_valid():
                    serializer.validated_data['delete_at'] = datetime.datetime.now()
                    serializer.save()

                    documents = Document.objects.filter(portfolio=portfolio)
                    for document in documents:
                        document.is_delete = True
                        document.delete_at = datetime.datetime.now()
                        document.save()

                    success_count += 1

            except Portfolio.DoesNotExist:
                pass

        if success_count > 0:
            data = {
                'status': 'success',
                'message': f'Deleted {success_count} portfolios and associated documents successfully'
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                'status': 'error',
                'message': 'Failed to delete portfolios and associated documents'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)        
        
        
        
        
        
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
        fields = ['name', 'parent_folder']





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
            queryset = queryset.filter(create_by=user, is_delete = False)
        return queryset 
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
        folder = self.get_folder(pk)
        folder.soft_delete(request)
        try:
            queryset = Folder.objects.filter(parent_folder = pk)
            serializer_db = FolderSerializer(queryset,many=True)
            data = serializer_db.data
            for i in data:
                self.delete(request,i['id'])
            folder.save()
            return Response({'status':200,
                             'message':'delete successfully'
                            }, status=status.HTTP_200_OK)
        except:
            return Response({'status':400}, status=status.HTTP_400_BAD_REQUEST)

class FolderDeletes(APIView):
    def delete(self, request, *args, **kwargs):
        selected_records = request.data.get('selected_records', [])
        queryset =  Folder.objects.filter(id__in=selected_records)
        serializers = FolderSerializer(queryset,many=True)
        try:
            for i in serializers.data:
                queryset_child = Folder.objects.filter(parent_folder = i['id'])
                serializer_child = FolderSerializer(queryset_child,many=True)
                for j in serializer_child.data:
                    self.delete(j['id'])
            return Response({'status':200},status=status.HTTP_200_OK)
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
            return [permissions.IsAuthenticated()]
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
        
class ShareUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
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
        return Response({'status':200, 'message':'updated successfully'},serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete=True
        instance.delete_at=datetime.now() 
        instance.delete_by=request.user
        self.perform_update(instance)
        return Response({'status':200,'message':'destroyed'},status=status.HTTP_204_NO_CONTENT)  

######WAREHOUSE######



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
        
        if warehouse.type_warehouse == ChoicesTypeWarehouse.Shelf.value:
            # Soft delete the shelf and its associated boxcases
            warehouse.is_delete = True
            warehouse.delete_at = timezone.now()  # Cập nhật delete_at với ngày và giờ hiện tại
            warehouse.save()
            
            shelf_boxcases = Warehouse.objects.filter(parent_warehouse=warehouse).prefetch_related('parent_warehouse')
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
            return Response({'status':400,
                             'message':'error'
                             },status=status.HTTP_400_BAD_REQUEST)
        return Response({'status':200,
                             'message':'delete successfully'},status=status.HTTP_200_OK)


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