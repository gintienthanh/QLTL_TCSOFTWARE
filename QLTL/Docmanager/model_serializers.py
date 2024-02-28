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
        
        

class WarehouseSerializer(serializers.ModelSerializer):
    parent_warehouse = serializers.SerializerMethodField()
    class Meta:
        model = Warehouse
        fields = '__all__'
        
    def get_parent_warehouse(self, obj):
        if obj.parent_warehouse:
            return WarehouseSerializer(obj.parent_warehouse).data
        return None
        
class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share
        fields = '__all__'
        
class ClassificationSerializer(serializers.ModelSerializer):
    class Meta: 
        model = ClassifyVariant
        fields = '__all__'
        