from rest_framework import serializers
from .models import Base,BoxCase,Shelf,Document,Portfolio,Warehouse,Folder,Watchlist

class BaseSerializers(serializers.ModelSerializer):
    class Meta:
        model = Base
        fields = ('base_id','is_visibale','is_delete','created_at','updated_at')

    # def create(self):
    #     Base.objects.create()


class WarehouseSerializers(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ('warehouse_id','name','user','warehouse_code','base',)

class ShelfSerializers(serializers.ModelSerializer):
    class Meta:
        model = Shelf
        fields = ('shelf_id','warehouse_id','name','base',)

class BoxCaseSerializers(serializers.ModelSerializer):
    class Meta:
        model = BoxCase
        fields = ('boxcase_id','warehouse_id','shelf_code','description','name','base',)


class DocumentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('document_id','folder_id','border_frame','usage_mode','storage_code','document_expiration','images_title','physical_status','info_additional','name','path','color','date','note','files','user','base',)

class PortfolioSerializers(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ('portfolio_id','identification_code','classification_id','retention_period','usage_mode','box_case_id','physical_condition','key_word','usage_mode','start_date','end_date','title','annotation','barcode','user','base',)

class FolderSerializers(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ('folder_id','shelf_id','warehouse_id','name','folder','boxcase','user','path','base',)

class WatchlistSerializers(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = ('watchlist_id','document_id','folder','user','base',)