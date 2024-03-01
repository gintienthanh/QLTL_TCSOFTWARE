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
from .views import *
from django.conf import settings
from django.conf.urls.static import static

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API documentation for your project",
        terms_of_service="https://quanlytailieu-be.tcgroup.vn/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

folder_urls = [
    path('', FolderList.as_view(), name='folder-list'),
    path('/<int:pk>', FolderUpdate.as_view(), name='folder-detail'),
]

warehouse_urls = [
    path('', WarehouseList.as_view(), name='warehouse-list'),
    path('/<int:pk>', WarehouseUpdate.as_view(), name='warehouse-detail'),
]

share_urls = [
    path('', ShareList.as_view(), name='share-list'),
    path('/<int:pk>', ShareUpdate.as_view(), name='share-detail'),
]

portfolio_urls = [
    path('', PortfolioList.as_view(), name='portfolio-list'),
    path('/<int:pk>', PortfolioUpdate.as_view(), name='portfolio-detail'),
    path('/multi_download/<str:ids>/', Multi_portfolio_DownloadConvertAPIView.as_view(), name='multi-portfolio-download'),
   
]

document_urls = [
    path('', DocumentList.as_view(), name='document-list'),
    path('/<int:pk>', DocumentUpdate.as_view(), name='document-detail'),
  
]

watchlist_urls = [
    path('', WatchList.as_view(), name='watchlist-list'),
    path('/<int:pk>', WatchListUpdate.as_view(), name='watchlist-detail'),
]

file_urls = [
    path('/download/<int:folder_id>/', DownloadFile.as_view(), name='file-download'),
]

urlpatterns = [
    path('folder', include((folder_urls, 'folder'))),
    path('warehouse', include((warehouse_urls, 'warehouse'))),
    path('share', include((share_urls, 'share'))),
    path('portfolio', include((portfolio_urls, 'portfolio'))),
    path('document', include((document_urls, 'document'))),
    path('watchlist', include((watchlist_urls, 'watchlist'))),
    path('file', include((file_urls, 'file'))),
    path('api/docs/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-swagger-json'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
