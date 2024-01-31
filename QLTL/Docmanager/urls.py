from django.urls import path
from . import views

urlpatterns = [
    path('warehouse/',views.WarehouseView.as_view(),name='view_warehouse'),
    path('<int:warehouse_id>/',views.WarehouseView.as_view(),name='view_warehouse'),
    path('shelf/',views.ShelfView.as_view(),name='view_warehouse'),
    path('<int:product_id>/',views.ShelfView.as_view(),name='view_warehouse'),
    path('boxcase/',views.BoxCaseView.as_view(),name='view_warehouse'),
    path('<int:boxcase_id>/',views.BoxCaseView.as_view(),name='view_warehouse'),
    path('watchlist/',views.WatchlistView.as_view(),name='view_warehouse'),
    path('<int:watchlist_id>/',views.WatchlistView.as_view(),name='view_warehouse'),
    path('document/',views.DocumentView.as_view(),name='view_warehouse'),
    path('<int:document_id>/',views.DocumentView.as_view(),name='view_warehouse'),
    path('folder/',views.FolderView.as_view(),name='view_warehouse'),
    path('<int:folder_id>/',views.FolderView.as_view(),name='view_warehouse'),
    path('portfolio/',views.PortfolioView.as_view(),name='view_warehouse'),
    path('<int:portfolio_id>/',views.PortfolioView.as_view(),name='view_warehouse'),
]
