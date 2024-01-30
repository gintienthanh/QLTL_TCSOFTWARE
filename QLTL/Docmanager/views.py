from django.shortcuts import render
from rest_framework import status,generics,serializers,permissions
from rest_framework.views import APIView, View
from rest_framework.response import Response
from .model_serializers import BaseSerializers,BoxCaseSerializers,ShelfSerializers,FolderSerializers,PortfolioSerializers,DocumentSerializers,WarehouseSerializers,WatchlistSerializers
from .models import Base,BoxCase,Shelf,Document,Portfolio,Warehouse,Folder,Watchlist

# Create your views here.

class BoxCaseView(generics.CreateAPIView):
    def get(self,request):
        queryset = BoxCase.objects.all()
        serializers = BoxCaseSerializers(queryset,many=True)
        return Response(serializers.data)
    