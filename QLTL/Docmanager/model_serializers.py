from rest_framework import serializers
from .models import *
from django_filters import rest_framework as filters
import django_filters
from django.contrib.auth.models import User,Permission,Group

class AdjustedNameField(serializers.CharField):
    def to_internal_value(self, data):
        model = self.parent.Meta.model
        # Kiểm tra và điều chỉnh tên trùng lặp
        existing_names = model.objects.filter(name__startswith=data).values_list('name', flat=True)

        if data in existing_names:
            i = 1
            while f"{data}({i})" in existing_names:
                i += 1
            data = f"{data}({i})"
        return data



class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Base
        fields = '__all__'


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
        
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'
class GroupSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Group
        fields = ['id', 'name']
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        
class ClassificationSerializer(serializers.ModelSerializer):
    class Meta: 
        model = ClassifyVariant
        fields = '__all__'

class RetentionPeriodSerializer(serializers.ModelSerializer):
    class Meta: 
        model = RetentionPeriod
        fields = '__all__'

class LanguageSerializer(serializers.ModelSerializer):
    
    class Meta: 
        model = Language
        fields = '__all__'
