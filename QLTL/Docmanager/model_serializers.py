from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User,Permission,Group

class AdjustedNameField(serializers.CharField): 
    def to_internal_value(self, data): 
        model = self.parent.Meta.model 
         
        
        if hasattr(model, 'title'): 
            existing_titles = model.objects.filter(title__startswith=data).values_list('title', flat=True) 
            if data in existing_titles: 
                i = 1 
                while f"{data}({i})" in existing_titles: 
                    i += 1 
                data = f"{data}({i})" 
                 
            return data 
         
        if hasattr(model, 'name'): 
            type_warehouse = self.parent.initial_data.get('type_warehouse') 
             
            if type_warehouse: 
                existing_names = model.objects.filter(type_warehouse=type_warehouse).values_list('name', flat=True) 
            else: 
                existing_names = model.objects.filter(name__startswith=data).values_list('name', flat=True) 
             
            if data in existing_names: 
                data = self.generate_unique_name(data, existing_names) 
         
        return data 
     
    def generate_unique_name(self, name, existing_names): 
        i = 1 
        new_name = name 
        while new_name in existing_names: 
            new_name = f"{name}({i})" 
            i += 1 
        return new_name


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
    # owner = UserSerializer(many=False, read_only=True)
    owner = serializers.SerializerMethodField()
    def get_owner(self,obj):
        # user = User.objects.get(id=obj.owner)
        return obj.owner.username

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