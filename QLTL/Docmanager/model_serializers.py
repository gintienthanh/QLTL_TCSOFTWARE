from rest_framework import serializers
from .models import *

class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Base
        fields = '__all__'
    

class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = '__all__'
        



class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'
        
class WatchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = '__all__'
        
        
# chặn thay đổi trường type_warehouse

from django.db.models import Max

class WarehouseSerializer(serializers.ModelSerializer):
    parent_warehouse = serializers.SerializerMethodField()
    class Meta:
        model = Warehouse
        fields = '__all__'
        
    def get_parent_warehouse(self, obj):
        if obj.parent_warehouse:
            return WarehouseSerializer(obj.parent_warehouse).data
        return None

    def validate_name(self, value):
        existing_names = Warehouse.objects.filter(name__startswith=value)
        if self.instance:  # Đối tượng đang được cập nhật
            existing_names = existing_names.exclude(pk=self.instance.pk)
        similar_names = existing_names.filter(name__regex=r'^{}(\((\d+)\))?$'.format(value))
        if similar_names.exists():
            counter = 1
            while similar_names.filter(name='{}({})'.format(value, counter)).exists():
                counter += 1
            value = '{}({})'.format(value, counter)
        return value
        
        
class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share
        fields = '__all__'
        
class ClassificationSerializer(serializers.ModelSerializer):
    class Meta: 
        model = ClassifyVariant
        fields = '__all__'
        # read_only_fields = ['created_at', 'updated_at','is_visibale']
