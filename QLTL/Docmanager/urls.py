from django.urls import path, include
from .views import*
urlpatterns = [
    path('folderlist', FolderList.as_view()),
    path('shelflist', ShelfList.as_view()),
    path('watchlist', WatchList.as_view()),
    path('boxcaselist', BoxCaseList.as_view()),
    path('warehouselist', WarehouseList.as_view()),
    path('portfoliolist', PortfolioList.as_view()),
    path('documentlist', DocumentList.as_view()),
]
