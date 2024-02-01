from rest_framework import serializers
from .models import *

class BaseSerializers(serializers.ModelSerializer):
    class Meta:
        model = Base
        fields = '__all__'
    # def create(self):
    #     Base.objects.create()


class WarehouseSerializers(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at','is_visibale','is_delete']
    
class ShelfSerializers(serializers.ModelSerializer):
    class Meta:
        model = Shelf
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at','is_visibale','is_delete']

class BoxCaseSerializers(serializers.ModelSerializer):
    class Meta:
        model = BoxCase 
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at','is_visibale','is_delete']


class DocumentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at','is_visibale','is_delete']

class PortfolioSerializers(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at','is_visibale','is_delete']

class FolderSerializers(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at','is_visibale','is_delete']

class WatchlistSerializers(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at','is_visibale','is_delete']
