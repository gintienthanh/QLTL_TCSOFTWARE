from django.urls import path, include
from .views import*
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('folder', FolderList.as_view()),
    path('folder/<int:pk>', FolderUpdate.as_view()),
    path('folder-filter/', FolderFilter.as_view()),
    
    path('warehouse', WarehouseList.as_view()),
    path('warehouse/<int:pk>', WarehouseUpdate.as_view()),
    
    
    path('share', ShareList.as_view()),
    path('share/<int:pk>', ShareUpdate.as_view()),
 
    
    path('portfolio', PortfolioList.as_view()),
    path('portfolio/<int:pk>', PortfolioUpdate.as_view()),
   
    
    path('document', DocumentList.as_view()),
    path('document/<int:pk>', DocumentUpdate.as_view()),
    
    
    
    path('watchlist', WatchList.as_view()),
    path('watchlist/<int:pk>', WatchListUpdate.as_view()),
    
    
    path('download/<int:pk>/', DownloadConvertAPIView.as_view(), name='download-convert'),
    path('multi_download_portfolio/<str:ids>/', Multi_portfolio_DownloadConvertAPIView.as_view(), name='Multi_portfolio_DownloadConvertAPIView'),
    path('file/download/<int:folder_id>', DownloadFile.as_view(), name='file-download'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
