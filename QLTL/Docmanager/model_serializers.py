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

class ClassifyVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassifyVariant
        fields = '__all__'


class WarehouseSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class WarehouseSimple1Serializer(serializers.ModelSerializer):
    subwarehouse = serializers.SerializerMethodField()

    def get_subwarehouse(self, obj):
        subwarehouses = obj.subwarehouse.all()
        serializer = WarehouseSimpleSerializer(subwarehouses, many=True)
        return serializer.data

    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'code', 'description', 'unit', 'type_warehouse', 'parent_warehouse', 'subwarehouse']


class AllWarehouseSerializer(serializers.ModelSerializer):
    subwarehouse = WarehouseSimple1Serializer(many=True)

    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'code', 'description', 'unit', 'type_warehouse', 'parent_warehouse', 'subwarehouse']

   




class FolderSerializer(serializers.ModelSerializer):
    parent_folder = serializers.PrimaryKeyRelatedField(required =False,read_only=True)
    file_size = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    
    def get_files(self, obj):
        if obj.type == 'File':
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri() + '/' + str(obj.id) + '/preview'
        return None
    
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
    
    def get_owner_name(self, obj):
        if obj.owner:
            return obj.owner.username
        else:
            return None
    
    
    class Meta:
        model = Folder
        fields = '__all__'



class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
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
    owner_infor = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = Share
        fields = '__all__'
     
    def get_owner_infor(self, obj):
        owner = obj.owner
        if owner:
            return {'id': owner.id, 'username': owner.username, 'email': owner.email}
        return None
        
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
        
class PortfolioSerializer(serializers.ModelSerializer): 
    title = AdjustedNameField() 
    docsubport = serializers.SerializerMethodField() 
    owner = serializers.SerializerMethodField(read_only = True)
    create_by = serializers.SerializerMethodField(read_only = True)
    
    def get_owner(self, obj):
        owner = obj.owner
        if owner:
            return {'id': owner.id, 'username': owner.username, 'email': owner.email}
        return None
    def get_create_by(self, obj):
        owner = obj.owner
        if owner:
            return {'id': owner.id, 'username': owner.username, 'email': owner.email}
        return None
    
     
    def get_docsubport(self, obj): 
        docsubports = Document.objects.filter(portfolio=obj,is_delete=False) 
        serializer = DocumentSerializer(docsubports, many=True) 
        return serializer.data 
    
    class Meta: 
        model = Portfolio 
        fields = ['id','title','retention_period', 'languege', 'classification','identification_code','usage_policy','start_date','end_date','physical_condition','warehouse','keywords','annotation','barcode','status', 'is_delete','created_at', 'updated_at', 'delete_at', 'owner','create_by','delete_by', 'editor', 'docsubport'] 
    def to_representation(self, instance): 
        data = super().to_representation(instance) 
        if instance.classification: 
            data['classification'] = ClassifyVariantSerializer(instance.classification).data 
        if instance.retention_period: 
            data['retention_period'] = RetentionPeriodSerializer(instance.retention_period).data 
        if instance.languege: 
            data['languege'] = LanguageSerializer(instance.languege).data 
        if instance.warehouse: 
            data['warehouse'] = WarehouseSerializer(instance.warehouse).data 
        return data
