from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User,Permission,Group

class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Base
        fields = '__all__'
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','username','is_active']

class FolderSerializer(serializers.ModelSerializer):
    parent_folder = serializers.PrimaryKeyRelatedField(required =False,read_only=True)
    file_size = serializers.SerializerMethodField()

    
    def get_file_size(self, obj):
        if obj.file_size == 0:
            return None
        elif obj.file_size is not None:
            size_in_mb = obj.file_size / (1024 * 1024)
            size_in_gb = obj.file_size / (1024 * 1024 * 1024)

            if size_in_gb >= 1:
                return f"{size_in_gb:.2f} GB"
            else:
                return f"{size_in_mb:.2f} MB"
        return None
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
        
