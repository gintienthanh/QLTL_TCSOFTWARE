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
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

folder_urls = [
    path('', FolderList.as_view(), name='folder-list'),
    path('<int:pk>', FolderUpdate.as_view(), name='folder-detail'),
]

warehouse_urls = [
    path('', WarehouseList.as_view(), name='warehouse-list'),
    path('<int:pk>', WarehouseUpdate.as_view(), name='warehouse-detail'),
]

share_urls = [
    path('', ShareList.as_view(), name='share-list'),
    path('<int:pk>', ShareUpdate.as_view(), name='share-detail'),
]

portfolio_urls = [
    path('', PortfolioList.as_view(), name='portfolio-list'),
    path('<int:pk>', PortfolioUpdate.as_view(), name='portfolio-detail'),
    path('multi_download/<str:ids>/', Multi_portfolio_DownloadConvertAPIView.as_view(), name='multi-portfolio-download'),
   
]

document_urls = [
    path('', DocumentList.as_view(), name='document-list'),
    path('<int:pk>', DocumentUpdate.as_view(), name='document-detail'),
  
]

watchlist_urls = [
    path('', WatchList.as_view(), name='watchlist-list'),
    path('<int:pk>', WatchListUpdate.as_view(), name='watchlist-detail'),
]

file_urls = [
    path('download/<int:folder_id>/', DownloadFile.as_view(), name='file-download'),
]

urlpatterns = [
    path('folder/', include((folder_urls, 'folder'))),
    path('warehouse/', include((warehouse_urls, 'warehouse'))),
    path('share/', include((share_urls, 'share'))),
    path('portfolio/', include((portfolio_urls, 'portfolio'))),
    path('document/', include((document_urls, 'document'))),
    path('watchlist/', include((watchlist_urls, 'watchlist'))),
    path('file/', include((file_urls, 'file'))),
    path('api/docs/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-swagger-json'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)