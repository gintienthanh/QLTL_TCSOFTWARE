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
import pandas as pd
import os
import zipfile
import tempfile
from io import BytesIO
from django.core.files.storage import default_storage
from rest_framework.decorators import permission_classes
# Create your views here.

class PortfolioList(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        portfolios = Portfolio.objects.filter(is_delete=False)
        serializer = PortfolioSerializer(portfolios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    
    
@permission_classes([CheckSharedGroupdFactory(Document(),'Chỉ xem')| CheckOwnerFactory(Document())])
class DocumentList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
@permission_classes([CheckSharedGroupdFactory(Document(),'Chỉnh sửa') | CheckOwnerFactory(Document())])
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
        folders = Folder.objects.filter(is_delete=False)
        serializer = FolderSerializer(folders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FolderSerializer(data=request.data)
        uploaded_file = request.FILES.get('files')
        files = request.FILES.getlist('files[]')
        name = request.POST.get('name')
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
                if parent_folder is not None:
            # Lưu tệp tin duy nhất
                    print(123109890823)
                    queryset = Folder.objects.filter(parent_folder = parent_folder)
                  

                    print(queryset)
                    if "(" in name and ")" in name:
                        name_add = self.extract_and_convert_to_integer(name)
                        print(name_add)
                    # else:
                    #     for i in serializer_12.data:
                    #         if name == i['name']:
                    #             name = name + "(1)"
                    #             print(name)
                    #             break
                    serializer.save(type='Folder')
                else:
                    print(123123)
                    serializer.save(type='Folder')
                # serializer.save(type='Folder')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def extract_and_convert_to_integer(string):
        # Tìm vị trí của dấu mở ngoặc và đóng ngoặc
        start_index = string.find('(')
        end_index = string.find(')')

        if start_index != -1 and end_index != -1:
            # Tách chuỗi trong dấu ngoặc
            substring = string[start_index+1:end_index]

            try:
                # Chuyển đổi chuỗi thành số nguyên
                integer_value = int(substring)
                return integer_value
            except ValueError:
                # Xử lý ngoại lệ nếu không thể chuyển đổi thành số nguyên
                print("Không thể chuyển đổi chuỗi thành số nguyên.")
        
        return None
            

@permission_classes([CheckSharedGroupdFactory(Folder(),'Chỉnh sửa') | CheckOwnerFactory(Folder())])
class FolderUpdate(APIView):
    permission_classes = [IsAuthenticated]
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
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
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
        serializer = FolderSerializer(folder, 
            data =
            {
                'is_delete': True,
                
            }, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class FolderFilter(generics.ListAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['name','file_size','parent_folder']

class ShareList(APIView):
    def get(self, request):
        share = Share.objects.filter(is_delete=False)
        serializer = ShareSerializer(share, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ShareSerializer(data=request.data)
        if serializer.is_valid():
            share = Share.objects.filter(folder=serializer.validated_data.get('folder'),
                                         document=serializer.validated_data.get('document'),
                                         create_by=request.user,
                                         owner=serializer.validated_data.get('owner'),
                                         type=serializer.validated_data.get('type')
                                         )
            if share.exists():
                share.update(create_by=request.user)
                updated_share = share.first()
                serializer = ShareSerializer(updated_share)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                serializer.save(create_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([CheckSharedGroupdFactory(Share(),'Chỉnh sửa') | CheckOwnerFactory(Share())])
class ShareUpdate(APIView):
    def get_object(self, pk):
        try:
            return Share.objects.get(pk=pk)
        except Share.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, pk):
        warehouse = self.get_object(pk)
        serializer = ShareSerializer(warehouse)
        return Response(serializer.data)

    
    def put(self, request, pk):
        share = self.get_object(pk)
        serializer = ShareSerializer(share, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        share = self.get_object(pk)
        serializer = ShareSerializer(share, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        share = self.get_object(pk)
        serializer = ShareSerializer(share, 
            data =
            {
                'is_delete': True,
                
            }, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class ShareFilter(generics.ListAPIView):
    queryset = Share.objects.all()
    serializer_class = ShareSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('owner', 'document','folder')


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
        type_warehouse = request.GET.get('type_warehouse')

        if type_warehouse == 'Giá Kệ':
            warehouse = Warehouse.objects.filter(type_warehouse='Giá Kệ')
        elif type_warehouse == 'Kho':
            warehouse = Warehouse.objects.filter(type_warehouse='Kho')
        elif type_warehouse == 'Hộp Cặp':
            warehouse = Warehouse.objects.filter(type_warehouse='Hộp cặp')
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
        serializer = WarehouseSerializer(warehouse, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        warehouse = self.get_object(pk)
        serializer = WarehouseSerializer(warehouse, data=request.data, partial=True)
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
    filterset_fields = ['name','type']



class WatchList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
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