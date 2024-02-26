from django.urls import path, include
from .views import*
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('folderlist', FolderList.as_view()),
    path('folderlist/<int:pk>', FolderUpdate.as_view()),
   
    path('warehouselist', WarehouseList.as_view()),
    path('warehouselist/<int:pk>', WarehouseUpdate.as_view()),
    path('warehouse_bulk_delete/<str:warehouse_ids>/', WarehouseBulkDelete.as_view(), name='warehouse_bulk_delete'),
       
    path('portfoliolist', PortfolioList.as_view()),
    path('portfoliolist/<int:pk>', PortfolioUpdate.as_view()),
    path('portfolio_bulk_delete/<str:portfolio_ids>/', PortfolioBulkDelete.as_view(), name='portfolio_bulk_delete'),

    
    path('documentlist', DocumentList.as_view()),
    path('documentlist/<int:pk>', DocumentUpdate.as_view()),
    path('document_bulk_delete/<str:document_ids>/', DocumentBulkDelete.as_view(), name='document_bulk_delete'),
    
    path('watchlist', WatchList.as_view()),
    
    path('portfoliolist/download/<int:pk>/', portfolio_DownloadConvertAPIView.as_view(), name='download-convert'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
