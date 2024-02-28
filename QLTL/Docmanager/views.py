import datetime
from django.shortcuts import render
from Docmanager.permissions import CheckOwnerFactory, CheckSharedGroupdFactory
from .model_serializers import*
from .models import*
from rest_framework import authentication, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
import mimetypes
import pandas as pd
from io import BytesIO
import zipfile
from django.core.files.storage import default_storage

# Create your views here.

class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        next_page = self.get_next_link()
        previous_page = self.get_previous_link()
        total_pages = self.page.paginator.num_pages
        current_page = self.page.number
        total_count = self.page.paginator.count
        return Response({
            'next_page': next_page,
            'previous_page': previous_page,
            'total_pages': total_pages,
            'current_page': current_page,
            'total_count': total_count,
            'results': data
        })
class PortfolioSetPagination(CustomPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000  
    
class FolderSetPagination(CustomPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000   
class WarehouseSetPagination(CustomPagination):
    page_size = 12
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


class PortfolioFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    usage_policy = filters.CharFilter(field_name='usage_policy', lookup_expr='icontains')
    
    class Meta:
        model = Portfolio
        fields = ['title', 'usage_policy']

class PortfolioList(generics.ListCreateAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Portfolio.objects.order_by('-updated_at')
    serializer_class = PortfolioSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = PortfolioFilter
    paginator = PortfolioSetPagination()
   
    
    def get_queryset(self):
        
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:  # Check if user is authenticated
            queryset = queryset.filter(create_by=user)
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

class PortfolioUpdate(APIView):
    #permission_classes = [permissions.IsAuthenticated]
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
            serializer.save()
            return Response({'status':201,
                             'message':'created successfully',
                             'data':serializer.data},status=status.HTTP_200_OK)
        return Response({'status':400,
                        'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        portfolio = self.get_object(pk)
        serializer = PortfolioSerializer(portfolio, 
            data =
            {   
                'is_delete': True,
                
            }, partial=True)
        if serializer.is_valid():
            serializer.validated_data['delete_at'] = datetime.datetime.now()
            serializer.save()
            return Response({'status':200,
                             'message':'delete successfully'
                            })
        return Response({'status':400,
                        'message':'delete Fail',
                        },status=status.HTTP_400_BAD_REQUEST)
    
class PortfolioFilter(generics.ListAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['title']

    

class DocumentList(generics.ListCreateAPIView):
    
    
    # def get_permissions(self):
    #     if self.request.method == 'POST':
    #         return [permissions.IsAuthenticated()]
    #     elif self.request.method == 'GET':
    #         return [permissions.IsAdminUser()]
    #     return super().get_permissions()
    def get(self, request , *args, **kwargs):
        paginator = DocumentSetPagination()
        document = Document.objects.filter(is_delete=False)
        document = document.order_by('-id')
        result_page = paginator.paginate_queryset(document, request)
        serializer = DocumentSerializer(result_page, many=True)
        
        data = {
            'status': '200',
            'message':'successfully',
            'pagination': {
                'count':paginator.page.paginator.count,
                'total_pages': paginator.page.paginator.num_pages,
                'current_page': paginator.page.number,
                'next_page': paginator.get_next_link(),
                'previous_page': paginator.get_previous_link(),
            },
            'data': serializer.data,
            
        }
        return Response(data, status=status.HTTP_200_OK)

class DocumentUpdate(generics.RetrieveUpdateDestroyAPIView):
    #permission_classes = [CheckSharedGroupdFactory(Document(),'edit') | CheckOwnerFactory(Document())]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response({'status':200,'message':'destroyed'},status=status.HTTP_204_NO_CONTENT)
 
class DocumentFilter(generics.ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['name']



class FolderList(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        paginator=FolderSetPagination()
        name_query = request.GET.get('name', None)  
       
        folder = Folder.objects.filter(is_delete=False, parent_folder=None)
    
        if name_query: 
             folder = folder.filter(name__icontains=name_query)
        
    
        result_page = paginator.paginate_queryset(folder, request)
        serializer = FolderSerializer(result_page, many=True)
        data = {
                'status': '200',
                'message':' found successfully',
                'pagination': {
                    'count':paginator.page.paginator.count,
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': paginator.page.number,
                    'next_page': paginator.get_next_link(),
                    'previous_page': paginator.get_previous_link(),
                },
                'data': serializer.data,
                
            }
        return Response(data, status=status.HTTP_200_OK)
        
    def extract_and_convert_to_integer(self,name,data):
        # Tìm vị trí của dấu mở ngoặc và đóng ngoặc
        start_index = name.rfind('(')
        end_index = name.rfind(')')
        if start_index != -1 and end_index != -1 and start_index < end_index:
            # Tách chuỗi trong dấu ngoặc
            try:
                name_list = []
                for i in data:
                    name_list.append(i['name'])
                print(name_list)
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
                # Xử lý ngoại lệ nếu không thể chuyển đổi thành số nguyên
                return name
        
        return None
    def post(self, request):
        serializer = FolderSerializer(data=request.data)
        uploaded_file = request.FILES.get('files')
        files = request.FILES.getlist('files[]')
        name = request.POST.get('name')
        name = name.rstrip()
        parent_folder = request.POST.get('parent_folder')
        if serializer.is_valid():
            if files:
                # Lưu danh sách các tệp tin
                files_list = []
                for file in files:
                    file_path = default_storage.save(file.name, file)
                    files_list.append(file)
                serializer.save(type='File', files=files_list,file_size = file.size,path = file_path)
            elif uploaded_file:
                    file_path = default_storage.save(uploaded_file.name, uploaded_file)
                    if name is not None:
                        serializer.save(type='File', files=uploaded_file,file_size = uploaded_file.size, path = file_path, name = name)
                    else:
                        serializer.save(type='File', files=uploaded_file,file_size = uploaded_file.size, path = file_path, name = file_path)
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
            return Response({'status':201,
                             'message':'created successfully',
                             'data':serializer.data},status=status.HTTP_201_CREATED)
        return Response({'status':400,
                             'message':'created fail',
                             'data':serializer.data},status=status.HTTP_400_BAD_REQUEST)

# @permission_classes([CheckSharedGroupdFactory(Folder(),'Chỉnh sửa') | CheckOwnerFactory(Folder())])
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
        return Response({'status':302,
                             'message':'found successfully',
                             'data':serializer.data},status=status.HTTP_302_FOUND)
    


    def patch(self, request, pk):
        folder = self.get_object(pk)
        serializer = FolderSerializer(folder, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':200,
                             'message':'update successfully'
                             },status=status.HTTP_200_OK)
        return Response({'status':400,
                             'message':'update fail'
                             },status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        folder = self.get_object(pk)
        serializer = FolderSerializer(folder, 
            data =
            {
                'is_delete': True,
                
            }, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':200,
                             'message':'delete successfully'},status=status.HTTP_200_OK)
        return Response({'status':400,
                            'message':serializer.errors,
                             },status=status.HTTP_400_BAD_REQUEST)
    
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
    # def get_permissions(self):
    #     if self.request.method == 'POST':
    #         return [permissions.IsAuthenticated()]
    #     elif self.request.method == 'GET':
    #         return [permissions.IsAuthenticated()]
    #     return super().get_permissions()
        
    def get(self, request):
        paginator = ShareSetPagination()
        share = Share.objects.filter(is_delete=False)
        result_page = paginator.paginate_queryset(share, request)
        serializer = PortfolioSerializer(result_page, many=True)
        data = {
            'status': '200',
            'message':'successfully',
            'pagination': {
                'count':paginator.page.paginator.count,
                'total_pages': paginator.page.paginator.num_pages,
                'current_page': paginator.page.number,
                'next_page': paginator.get_next_link(),
                'previous_page': paginator.get_previous_link(),
            },
            'data': serializer.data,
            
        }
        return Response(data, status=status.HTTP_200_OK)

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
                    return Response({'status':201,
                             'message':'created successfully',
                             'data':serializer.data},status=status.HTTP_201_CREATED)
                except Share.DoesNotExist:
                    serializer.save(create_by=request.user)
                    return Response({'status':201,
                             'message':'created successfully',
                             'data':serializer.data},status=status.HTTP_201_CREATED)
            return Response({'status':400,
                             'message':'created fail'
                            },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status':400,'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class ShareUpdate(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [CheckSharedGroupdFactory(Share(),'edit') | CheckOwnerFactory(Share())]
    queryset = Share.objects.all()
    serializer_class = ShareSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response({'status':200,'message':'destroyed'},status=status.HTTP_204_NO_CONTENT)

class WarehouseList(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        paginator = WarehouseSetPagination()
        type_warehouse = request.GET.get('type_warehouse', None)
        warehouse = Warehouse.objects.filter(is_delete=False)
        if type_warehouse == 'shelf':
            warehouse = Warehouse.objects.filter(type_warehouse='shelf',is_delete=False)
        elif type_warehouse == 'warehouse':
            warehouse = Warehouse.objects.filter(type_warehouse='warehouse', is_delete=False)
        elif type_warehouse == 'boxcase':
            warehouse = Warehouse.objects.filter(type_warehouse='boxcase', is_delete=False)
        else:
            return Response({"error": "Invalid type_warehouse value"}, status=status.HTTP_400_BAD_REQUEST)
        result_page = paginator.paginate_queryset(warehouse, request)
        
        serializer = WarehouseSerializer(result_page, many=True)
        
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
            
            
            
            

class WarehouseUpdate(APIView):
    permission_classes = [permissions.IsAuthenticated]
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
        serializer = WarehouseSerializer(warehouse, 
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

class WarehouseFilter(generics.ListAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['name','type_warehouse', 'parent_warehouse']



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
        try:
            file = Folder.objects.get(pk=folder_id)
            file_path = file.files.path
            content_type, encoding = mimetypes.guess_type(file_path)
            content_type = content_type or 'application/octet-stream'
            response = HttpResponse(open(file_path, 'rb'), content_type=content_type)
            # Tạo response từ tệp tin
            response['Content-Disposition'] = f'attachment; filename="{file.files.name}"'
            print(file_path)
            # shutil.copy2(file_path, save_path)
            return response
        except Folder.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

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

# class DocumentFolder(APIView)
                                                                                           
