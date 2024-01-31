from django.urls import path
from . import views

urlpatterns = [
    path('warehouse/',views.WarehouseView.as_view(),name='view_warehouse'),
    path('<int:warehouse_id>/',views.Warehouse_IDView.as_view(),name='view_warehouse_ID'),
    path('shelf/',views.ShelfView.as_view(),name='view_shelf'),
    path('<int:product_id>/',views.Shelf_IDView.as_view(),name='view_shelf_ID'),
    path('boxcase/',views.BoxCaseView.as_view(),name='view_boxcase'),
    path('<int:boxcase_id>/',views.BoxCase_IDView.as_view(),name='view_boxcase_ID'),
    path('document/',views.DocumentView.as_view(),name='view_document'),
    path('<int:document_id>/',views.Document_IDView.as_view(),name='view_document_ID'),
    path('portfolio/',views.PortfolioView.as_view(),name='view_portfolio'),
    path('<int:portfolio_id>/',views.Portfolio_IDView.as_view(),name='view_portfolio_ID'),
    path('folder/',views.FolderView.as_view(),name='view_folder'),
    path('<int:folder_id>/',views.Folder_IDView.as_view(),name='view_folder_ID'),
    path('watchlist/',views.WatchlistView.as_view(),name='view_watchlist'),
    path('<int:watchlist_id>/',views.Watchlist_IDView.as_view(),name='view_watchlist_ID'),
]
