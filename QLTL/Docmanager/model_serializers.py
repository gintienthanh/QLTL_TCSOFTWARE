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
    documents = serializers.SerializerMethodField()  # Thay thế DocumentSerializer bằng SerializerMethodField

    class Meta:
        model = Portfolio
        fields = '__all__'

    def get_documents(self, obj):
        documents = Document.objects.filter(portfolio=obj)
        serializer = DocumentSerializer(documents, many=True)
        return serializer.data

class WatchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = '__all__'

class BoxcaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxCase
        fields = '__all__'
        

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'
        
class ShelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelf
        fields = '__all__'