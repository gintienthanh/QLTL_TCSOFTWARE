from django.urls import path, include
from .views import*
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('folder', FolderList.as_view()),
    path('folder/<int:pk>', FolderUpdate.as_view()),
    path('folder-filter/', FolderList.as_view()),
    
    path('warehouse', WarehouseList.as_view()),
    path('warehouse/<int:pk>', WarehouseUpdate.as_view()),
    path('warehouse-filter/', WarehouseList.as_view()),
    path('WarehouseBulkDelete/<str:id>/', WarehouseBulkDelete.as_view(), name='WarehouseBulkDelete'),

    
    path('share', ShareList.as_view()),
    path('share/<int:pk>', ShareUpdate.as_view()),
 
    
    path('portfolio', PortfolioList.as_view()),
    path('portfolio/<int:pk>', PortfolioUpdate.as_view()),
    path('portfolio-filter/', PortfolioFilter.as_view()),
    path('multi_download_portfolio/<str:ids>/', Multi_portfolio_DownloadConvertAPIView.as_view(), name='Multi_portfolio_DownloadConvertAPIView'),
    path('download_portfolio/<int:pk>/', portfolio_DownloadConvertAPIView.as_view(), name='portfolio_DownloadConvertAPIView-convert'),
    path('bulk_delete/<str:id>/', PortfolioBulkUpdate.as_view(), name='portfolio_bulk_delete'),
    
    
    path('document', DocumentList.as_view()),
    path('document/<int:pk>', DocumentUpdate.as_view()),
    path('document-filter/', DocumentList.as_view()),
    
    
    path('watchlist', WatchList.as_view()),
    path('watchlist/<int:pk>', WatchListUpdate.as_view()),
    
    path('file/download/<int:folder_id>', DownloadFile.as_view(), name='file-download'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
