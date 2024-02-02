from django.urls import path
from . import views

urlpatterns = [
    path('warehouse/',views.WarehouseView.as_view(),name='view_warehouse'),
    path('warehouse/<int:warehouse_id>/',views.Warehouse_IDView.as_view(),name='view_warehouse_ID'),

    path('shelf/',views.ShelfView.as_view(),name='view_shelf'),
    path('shelf/<int:product_id>/',views.Shelf_IDView.as_view(),name='view_shelf_ID'),

    path('boxcase/',views.BoxCaseView.as_view(),name='view_boxcase'),
    path('boxcase/<int:boxcase_id>/',views.BoxCase_IDView.as_view(),name='view_boxcase_ID'),

    path('document/',views.DocumentView.as_view(),name='view_document'),
    path('document/<int:document_id>/',views.Document_IDView.as_view(),name='view_document_ID'),

    path('portfolio/',views.PortfolioView.as_view(),name='view_portfolio'),
    path('portfolio/<int:portfolio_id>/',views.Portfolio_IDView.as_view(),name='view_portfolio_ID'),

    path('folder/',views.FolderView.as_view(),name='view_folder'),
    path('folder/<int:folder_id>/',views.Folder_IDView.as_view(),name='view_folder_ID'),
    path('folders/<int:child_folder>',views.FolderChildView.as_view(),name='child_folder'),

    path('watchlist/',views.WatchlistView.as_view(),name='view_watchlist'),
    path('watchlist/<int:watchlist_id>/',views.Watchlist_IDView.as_view(),name='view_watchlist_ID'),

    # path('download/<int:document_id>',views.DownloadFile.as_view(),name='view_watchlist'),
    path('document/download/<int:document_id>', views.DownloadFile.as_view(), name='file-download'),
    path('folder/download/<int:folder_id>', views.Downloadfolder.as_view(), name='folder-download'),
    path('search/',views.Search.as_view(),name='search'),

]
