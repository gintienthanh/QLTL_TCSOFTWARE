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
    path('', FolderListCreate.as_view(), name='folder-list'),
    path('/<int:pk>', FolderUpdateDelete.as_view(), name='folder-detail'),
]

warehouse_urls = [
    path('', WarehouseListCreate.as_view(), name='warehouse-list'),
    path('/<int:pk>', WarehouseUpdateDelete.as_view(), name='warehouse-detail'),
]

share_urls = [
    path('', APIShareListCreate.as_view(), name='share-list'),
    path('/<int:pk>', APIShareUpdateDestroy.as_view(), name='share-detail'),
]
permission_urls = [
    path('', APIPermissionListCreate.as_view(), name='permission-list'),
    path('/<int:pk>', APIPermissionUpdateDestroy.as_view(), name='permission-detail'),
    path('/user_permissions/<int:pk>/', UserPermissionView.as_view(), name='user-permissions'),
    path('/not_included_in_group/<int:pk>/', PermissionNotIncludedInGroup.as_view(), name='permission_not_included_in_group'),
]
group_urls = [
    path('', APIGroupListCreate.as_view(), name='group-list'),
    path('/<int:pk>', APIGroupUpdateDestroy.as_view(), name='group-detail'),
    path('/user_groups/<int:pk>/', GroupUserView.as_view(), name='group-users'),
    path('/group_permissions/<int:pk>/', GroupPermissionView.as_view(), name='group-permissions'),
]

portfolio_urls = [
    path('', PortfolioListCreate.as_view(), name='portfolio-list'),
    path('/<int:pk>', PortfolioUpdateDelete.as_view(), name='portfolio-detail'),
    path('/multi_download/<str:ids>/', Multi_portfolio_DownloadConvertAPIView.as_view(), name='multi-portfolio-download'),
   
]

document_urls = [
    path('', DocumentListCreate.as_view(), name='document-list'),
    path('/<int:pk>', DocumentUpdateDelete.as_view(), name='document-detail'),
  
]
user_urls = [
    path('', UserListCreate.as_view(), name='user-listcreate'),
    path('/<int:pk>', UserUpdateDelete.as_view(), name='document-list'),
  
]

watchlist_urls = [
    path('', WatchListCreate.as_view(), name='watchlist-list'),
    path('/<int:pk>', WatchListUpdateDelete.as_view(), name='watchlist-detail'),
]

file_urls = [
    path('download/<int:folder_id>/', DownloadFile.as_view(), name='file-download'),
]
user_urls =  [
    path('userlist/',UserListApiView.as_view(),name="userlist"),
   
]



retentionperiod_urls = [
    path('', RetentionPeriodListCreate.as_view(), name='storagetime-list'),
    path('/<int:pk>', RetentionPeriodUpdateDelete.as_view(), name='storagetime-detail'),
    
]

language_urls = [
    path('', LanguageListCreate.as_view(), name='language-list'),
    path('/<int:pk>', LanguageUpdateDelete.as_view(), name='language-detail'),
    
]





urlpatterns = [
    path('folder', include((folder_urls, 'folder'))),
    path('warehouse', include((warehouse_urls, 'warehouse'))),
    path('share', include((share_urls, 'share'))),
    path('permission', include((permission_urls, 'permission'))),
    path('group', include((group_urls, 'group'))),
    path('portfolio', include((portfolio_urls, 'portfolio'))),
    path('document', include((document_urls, 'document'))),
    path('user', include((user_urls, 'user'))),
    path('watchlist', include((watchlist_urls, 'watchlist'))),
    path('user/',include((user_urls, 'userurl'))),
    path('retentionperiod', include((retentionperiod_urls, 'storagetime'))),
    path('language', include((language_urls, 'language'))),
    
    
    path('file/', include((file_urls, 'file'))),
    path('docs/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-swagger-json'),
    path('docs', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('bulk_delete/', BulkDeleteAPI.as_view(), name='portfolio-bulk-delete'),



    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)