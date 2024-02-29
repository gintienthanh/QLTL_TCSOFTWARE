from django.urls import path, include
from .views import*
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


urlpatterns = [
    path('folder', FolderList.as_view()),
    path('folder/<int:pk>', FolderUpdate.as_view()),
    
    
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
    
    path('api/docs/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-swagger-json'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
