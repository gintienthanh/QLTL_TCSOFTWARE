from django.urls import path, include
from .views import*
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('folderlist', FolderList.as_view()),
    path('folderlist/<int:pk>', FolderUpdate.as_view()),
   
    path('warehouselist', WarehouseList.as_view()),
    path('warehouselist/<int:pk>', WarehouseUpdate.as_view()),
   
    path('portfoliolist', PortfolioList.as_view()),
    path('portfoliolist/<int:pk>', PortfolioUpdate.as_view()),
    
    path('documentlist', DocumentList.as_view()),
    path('documentlist/<int:pk>', DocumentUpdate.as_view()),
    
    path('watchlist', WatchList.as_view()),
    
    path('download/<int:pk>/', DownloadConvertAPIView.as_view(), name='download-convert'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
