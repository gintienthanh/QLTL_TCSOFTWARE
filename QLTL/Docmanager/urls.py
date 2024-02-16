from django.urls import path, include
from .views import*
urlpatterns = [
    path('folderlist', FolderList.as_view()),
    path('folderlist/<int:pk>', FolderUpdate.as_view()),
    
    
    path('shelflist', ShelfList.as_view()),
    path('shelflist/<int:pk>', ShelfUpdate.as_view()),
    
    
    path('watchlist', WatchList.as_view()),
    path('watchlist/<int:pk>', WatchlistUpdate.as_view()),
    
    
    path('boxcaselist', BoxCaseList.as_view()),
    path('boxcaselist/<int:pk>', BoxCaseUpdate.as_view()),
    
    path('warehouselist', WarehouseList.as_view()),
    path('warehouselist/<int:pk>', WarehouseUpdate.as_view()),
    
    
    path('portfoliolist', PortfolioList.as_view()),
    path('portfoliolist/<int:pk>', PortfolioUpdate.as_view()),
    
    path('documentlist', DocumentList.as_view()),
    path('documentlist/<int:pk>', DocumentUpdate.as_view()),
    
    path('download/<int:pk>/', DownloadConvertAPIView.as_view(), name='download-convert'),

]
