from rest_framework import serializers
from .models import *

class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Base
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at','is_visibale','is_delete']

class FolderSerializer(serializers.ModelSerializer):
    parent_folder = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at','is_visibale','is_delete']

    def get_parent_folder(self, obj):
        if obj.parent_folder:
            return FolderSerializer(obj.parent_folder).data
        return None


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at','is_visibale']

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at','is_visibale']
class WatchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at','is_visibale']
        
# chặn thay đổi trường type_warehouse

from django.db.models import Max

class WarehouseSerializer(serializers.ModelSerializer):
    parent_warehouse = serializers.SerializerMethodField()
    class Meta:
        model = Warehouse
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at','is_visibale']
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
        read_only_fields = ['created_at', 'updated_at','is_visibale']
        
class ClassificationSerializer(serializers.ModelSerializer):
    class Meta: 
        model = ClassifyVariant
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at','is_visibale']
