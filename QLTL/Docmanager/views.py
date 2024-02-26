import os
from django.shortcuts import render
from QLTL import settings
from .model_serializers import*
from .models import*
from rest_framework import authentication, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
import pandas as pd
from io import BytesIO
import zipfile
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404
from rest_framework.pagination import PageNumberPagination


class WarehousePagination(PageNumberPagination):
    page_size = 4 # Số lượng phần tử trên mỗi trang
    page_size_query_param = 'page_size'
    max_page_size = 100

# Create your views here.
class PortfolioList(generics.ListCreateAPIView):
    serializer_class = PortfolioSerializer

    def get_queryset(self):
        return Portfolio.objects.filter(is_delete=False)


class PortfolioUpdate(generics.RetrieveUpdateDestroyAPIView):
    # queryset = Portfolio.objects.all()
    
    queryset = Portfolio.objects.filter(is_delete=False)
    serializer_class = PortfolioSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PortfolioBulkDelete(APIView):
    def delete(self, request, portfolio_ids, *args, **kwargs):
        portfolio_ids_list = portfolio_ids.split(',')
        for portfolio_id in portfolio_ids_list:
            try:
                portfolio = Portfolio.objects.get(id=int(portfolio_id))
                portfolio.is_delete = True
                portfolio.save()
            except Portfolio.DoesNotExist:
                pass
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class DocumentList(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer

    def get_queryset(self):
        return Document.objects.filter(is_delete=False)
    
    
class DocumentUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
# xoá hàng loạt
class DocumentBulkDelete(APIView):
    def delete(self, request, document_ids, *args, **kwargs):
        document_ids_list = document_ids.split(',')
        for document_id in document_ids_list:
            try:
                document = Document.objects.get(id=int(document_id))
                document.is_delete = True
                document.save()
            except Document.DoesNotExist:
                pass
        return Response(status=status.HTTP_204_NO_CONTENT)

class FolderList(APIView):
    def get(self, request):
        folders = Folder.objects.all()
        serializer = FolderSerializer(folders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FolderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FolderUpdate(APIView):
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
        folder.is_deleted = True
        folder.save()
        return Response(status=status.HTTP_204_NO_CONTENT)




class WarehouseList(APIView):
    def get(self, request):
        warehouses = Warehouse.objects.filter(is_delete=False)

        # Phân trang kết quả
        paginator = WarehousePagination()
        result_page = paginator.paginate_queryset(warehouses, request)
        serializer = WarehouseSerializer(result_page, many=True)

        data = {
            'status': '200',
            'data': serializer.data,
            'pagination': {
                'total_pages': paginator.page.paginator.num_pages,
                'current_page': paginator.page.number,
                'next_page': paginator.get_next_link(),
                'previous_page': paginator.get_previous_link(),
            }
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = WarehouseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                'status': '200',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = {
                'status': '400',
                'errors': serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

class WarehouseUpdate(APIView):
    def get_object(self, pk):
        try:
            return Warehouse.objects.get(pk=pk, is_delete=False)
        except Warehouse.DoesNotExist:
            raise Http404("Warehouse not found")

    def get(self, request, pk):
        try:
            warehouse = self.get_object(pk)
            serializer = WarehouseSerializer(warehouse)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404 as e:
            data = {
                'status': '400',
                'error': str(e)
            }
            return Response(data, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        warehouse = self.get_object(pk)
        serializer = WarehouseSerializer(warehouse, data=request.data)
        if serializer.is_valid():
            if 'type_warehouse' in serializer.validated_data:
                return Response({'error': 'Changing type warehouse is not allowed.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            data = {
                'status': 'success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                'status': 'error',
                'errors': serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        warehouse = self.get_object(pk)
        serializer = WarehouseSerializer(warehouse, data=request.data, partial=True)
        if serializer.is_valid():
            if 'type_warehouse' in serializer.validated_data:
                return Response({'error': 'Changing type warehouse is not allowed.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            data = {
                'status': 'success',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                'status': 'error',
                'errors': serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
            warehouse = self.get_object(pk)
            warehouse.is_deleted = True
            warehouse.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

class WarehouseBulkDelete(APIView):
    def delete(self, request, warehouse_ids, *args, **kwargs):
        warehouse_ids_list = warehouse_ids.split(',')
        for warehouse_id in warehouse_ids_list:
            try:
                warehouse = Warehouse.objects.get(id=int(warehouse_id))
                warehouse.is_delete = True
                warehouse.save()
            except Warehouse.DoesNotExist:
                pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class WatchList(APIView):
    def get(self, request):
        watchlists = Watchlist.objects.all()
        serializer = WatchListSerializer(watchlists, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WatchListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            watchlist = Watchlist.objects.get(pk=pk)
        except Watchlist.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = WatchListSerializer(watchlist, data=request.data)
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
    


class portfolio_DownloadConvertAPIView(generics.RetrieveAPIView):
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
                # 'box_case': document.box_case.name,
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

            # Thêm trường files vào file zip
            documents = Document.objects.filter(portfolio=portfolio)
            documents_data = []
            for document in documents:
                file_path = os.path.join(settings.MEDIA_ROOT, str(document.files))
                arcname = os.path.basename(str(document.files))
                zf.write(file_path, arcname=arcname)

        zip_file.seek(0)

        response = HttpResponse(zip_file.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=data.zip'
        
        return response

                                                                                            
