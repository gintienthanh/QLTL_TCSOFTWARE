from django.shortcuts import render
from .model_serializers import*
from .models import*
from rest_framework import authentication, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
# Create your views here.
import pandas as pd
from io import BytesIO
import zipfile
from django.http import HttpResponse
import os
from django.conf import settings

class PortfolioList(generics.ListCreateAPIView):
    serializer_class = PortfolioSerializer

    def get_queryset(self):
        return Portfolio.objects.filter(is_delete=False)
    
    
class PortfolioUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DownloadConvertAPIView(generics.RetrieveAPIView):
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

            # Thêm trường files vào file zip
            for document in documents:
                file_path = os.path.join(settings.MEDIA_ROOT, str(document.files))
                arcname = os.path.basename(str(document.files))
                zf.write(file_path, arcname=arcname)

        zip_file.seek(0)

        response = HttpResponse(zip_file.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=data.zip'
        return response
    
class DocumentList(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    
class DocumentUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class FolderList(generics.ListCreateAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    
    
    
class FolderUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class BoxCaseList(generics.ListCreateAPIView):
    queryset = BoxCase.objects.all()
    serializer_class = BoxcaseSerializer

class BoxCaseUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoxCase.objects.all()
    serializer_class = BoxcaseSerializer
    
class ShelfList(generics.ListCreateAPIView):
    queryset = Shelf.objects.all()
    serializer_class = ShelfSerializer

class ShelfUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shelf.objects.all()
    serializer_class = ShelfSerializer
    
    
class WarehouseList(generics.ListCreateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    
class WarehouseUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    
    
    
class WatchList(generics.ListCreateAPIView):
    queryset = Watchlist.objects.all()
    serializer_class = WatchListSerializer
                                                                                            
class WatchlistUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = BoxCase.objects.all()
    serializer_class = WarehouseSerializer
    