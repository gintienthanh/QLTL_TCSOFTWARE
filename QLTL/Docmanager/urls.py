# from django.urls import path
# from . import views

# urlpatterns = [
#     path('warehouse/',views.WarehouseView.as_view(),name='view_warehouse'),
#     path('warehouse/<int:warehouse_id>/',views.Warehouse_IDView.as_view(),name='view_warehouse_ID'),

#     path('shelf/',views.ShelfView.as_view(),name='view_shelf'),
#     path('shelf/<int:product_id>/',views.Shelf_IDView.as_view(),name='view_shelf_ID'),

#     path('boxcase/',views.BoxCaseView.as_view(),name='view_boxcase'),
#     path('boxcase/<int:boxcase_id>/',views.BoxCase_IDView.as_view(),name='view_boxcase_ID'),

#     path('document/',views.DocumentView.as_view(),name='view_document'),
#     path('document/<int:document_id>/',views.Document_IDView.as_view(),name='view_document_ID'),

#     path('portfolio/',views.PortfolioView.as_view(),name='view_portfolio'),
#     path('portfolio/<int:portfolio_id>/',views.Portfolio_IDView.as_view(),name='view_portfolio_ID'),

#     path('folders/',views.FolderView.as_view(),name='view_folder'),
#     path('folder/<int:folder_id>/',views.Folder_IDView.as_view(),name='view_folder_ID'),
#     path('folderlist/<int:child_folder>',views.FolderChildView.as_view(),name='child_folder'),

#     path('watchlist/',views.WatchlistView.as_view(),name='view_watchlist'),
#     path('watchlist/<int:watchlist_id>/',views.Watchlist_IDView.as_view(),name='view_watchlist_ID'),

#     # path('download/<int:document_id>',views.DownloadFile.as_view(),name='view_watchlist'),
#     path('document/download/<int:document_id>', views.DownloadFile.as_view(), name='file-download'),
#     path('folder/download/<int:folder_id>', views.Downloadfolder.as_view(), name='folder-download'),
#     path('search/',views.Search.as_view(),name='search'),
# ]

from django.urls import path, include
from .views import*
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('folder', FolderList.as_view(), name='folder'),
    path('folder/<int:pk>', FolderUpdate.as_view()),
    path('folder-filter/', FolderFilter.as_view()),
    path('folderparent/<int:parent_folder>', FolderParentView.as_view()),
    
    path('warehouse', WarehouseList.as_view()),
    path('warehouse/<int:pk>', WarehouseUpdate.as_view()),
    path('warehouse-filter/', WarehouseFilter.as_view()),
    
    path('share', ShareList.as_view()),
    path('share/<int:pk>', ShareUpdate.as_view()),
    path('share-filter/', ShareFilter.as_view()),
    
    path('portfolio', PortfolioList.as_view()),
    path('portfolio/<int:pk>', PortfolioUpdate.as_view()),
    path('portfolio-filter/', PortfolioFilter.as_view()),
    
    path('document', DocumentList.as_view()),
    path('document/<int:pk>', DocumentUpdate.as_view()),
    path('document-filter/', DocumentFilter.as_view()),
    
    
    path('watchlist', WatchList.as_view()),
    
    path('download/<int:pk>/', DownloadConvertAPIView.as_view(), name='download-convert'),
    path('file/download/<int:folder_id>', DownloadFile.as_view(), name='file-download'),
    path('folder/download/<int:pk>', DownloadFolder.as_view(), name='folder-download'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
