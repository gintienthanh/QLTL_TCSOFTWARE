from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

# Create your models here.
class Base(models.Models):
    base_id = models.AutoField(primary_key=True)
    is_visibale = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Warehouse(models.Model):
    name = models.CharField(max_length = 255, null = True, blank = True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    warehouse_code = models.CharField(max_length = 255, null = True, blank = True)
    base = models.ForeignKey(Base,on_delete=models.SET_NULL)

class Shelf(models.Model):
    name = models.CharField(max_length = 255, null = True, blank = True)
    warehouse_id = models.ForeignKey(Warehouse,on_delete=models.CASCADE, null=True, blank=True)
    base = models.ForeignKey(Base,on_delete=models.SET_NULL)

class BoxCase(models.Model):
    description = models.CharField(max_length = 255)
    name = models.CharField(max_length = 255, null = True, blank = True)
    warehouse_id = models.ForeignKey(Warehouse,on_delete=models.CASCADE, null=True, blank=True)
    shelf_code = models.CharField(max_length = 255, null = True, blank = True)
    base = models.ForeignKey(Base,on_delete=models.SET_NULL)


class Folder(models.Model):
    name = models.CharField()
    folder_id = models.ForeignKey('self',on_delete=models.CASCADE, null=True, blank=True)
    boxcase = models.ForeignKey(BoxCase,on_delete=models.CASCADE, null=True, blank=True)
    shelf_id = models.ForeignKey(Shelf,on_delete=models.CASCADE, null=True, blank=True)
    warehouse_id = models.ForeignKey(Warehouse,on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length = 255, null = True, blank = True)
    base = models.ForeignKey(Base,on_delete=models.SET_NULL)


class Document(models.Model):
    MODE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]
    BORDER_FRAME_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]
    name = models.CharField(max_length = 255, null = True, blank = True)
    path = models.CharField(max_length = 255, null = True, blank = True)
    folder_id = models.ForeignKey(Folder,on_delete = models.CASCADE)
    border_frame = models.CharField(choices=MODE_CHOICES)
    color = models.CharField(max_length = 10, null = True, blank = True)
    usage_mode = models.CharField(choices=MODE_CHOICES)
    storage_code = models.CharField(max_length = 255, null = True, blank = True)
    document_expiration = models.DateTimeField(default= timezone.datetime.now())
    images_title = models.CharField(max_length = 255, null = True, blank = True)
    date = models.DateTimeField(default= timezone.datetime.now())
    physical_status = models.CharField(max_length = 255, null = True, blank = True)
    note = models.CharField(max_length = 255, null = True, blank = True)
    files = models.FileField(null = True, blank = True)
    info_additional = models.CharField(max_length = 255, null = True, blank = True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    base = models.ForeignKey(Base,on_delete=models.SET_NULL)

class Portfolio(models.Model):
    MODE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]
    STATUS_CHOICES = [
        ('A', 'Chờ Duyệt'),
        ('B', 'Hoàn Thành'),
        ('C', 'Thất Bại'),
    ]

    title = models.CharField(max_length = 255, null = True, blank = True)
    identification_code = models.CharField(max_length = 255, null = True, blank = True)
    classification_id = models.CharField(max_length = 255, null = True, blank = True)
    retention_period = models.CharField(max_length = 255, null = True, blank = True)
    usage_mode = models.CharField(choices=MODE_CHOICES)
    box_case_id = models.ForeignKey(BoxCase,on_delete = models.CASCADE)
    physical_condition = models.CharField(max_length = 255, null = True, blank = True)
    key_word = models.CharField(max_length = 255, null = True, blank = True)
    annotation = models.CharField(max_length = 255, null = True, blank = True)
    barcode = models.CharField(max_length = 255, null = True, blank = True)
    usage_mode = models.CharField(choices=STATUS_CHOICES)
    start_date = models.DateTimeField(default = timezone.datetime.now())
    end_date = models.DateTimeField(default = timezone.datetime.now())
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    base = models.ForeignKey(Base,on_delete=models.SET_NULL)


class watchlist(models.Model):
    document_id = models.ForeignKey(Document, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    base = models.ForeignKey(Base,on_delete=models.SET_NULL)
    