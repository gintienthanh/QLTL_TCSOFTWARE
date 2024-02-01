from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

# Create your models here.
class Base(models.Model):
    is_visibale = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(default = timezone.datetime.now())
    updated_at = models.DateTimeField(default = timezone.datetime.now())
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        
class Warehouse(Base):
    warehouse_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length = 255, null = True, blank = True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    warehouse_code = models.CharField(max_length = 255, null = True, blank = True)

class Shelf(Base):
    shelf_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length = 255, null = True, blank = True)
    warehouse = models.ForeignKey(Warehouse,related_name='shelf_warehouse',on_delete=models.CASCADE, null=True, blank=True)

class BoxCase(Base):
    boxcase_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length = 255,null = True, blank = True)
    name = models.CharField(max_length = 255, null = True, blank = True)
    warehouse = models.ForeignKey(Warehouse,related_name='boxcase_warehouse',on_delete=models.CASCADE, null=True, blank=True)
    shelf_code = models.CharField(max_length = 255, null = True, blank = True)


class Folder(Base):
    folder_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length = 255, null = True, blank = True)
    child_folder = models.ForeignKey('self',related_name='folders',on_delete=models.CASCADE, null=True, blank=True)
    boxcase = models.ForeignKey(BoxCase,related_name='folder_boxcase',on_delete=models.CASCADE, null=True, blank=True)
    shelf = models.ForeignKey(Shelf,related_name='folder_shelf',on_delete=models.CASCADE, null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse,related_name='folder_warehouse',on_delete=models.CASCADE, null=True, blank=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length = 255, null = True, blank = True)


class Document(Base):
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
    DOCUMENT_EXPIRATION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]
    document_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length = 255, null = True, blank = True)
    path = models.CharField(max_length = 255, null = True, blank = True)
    folder = models.ForeignKey(Folder,related_name='document_folder',on_delete = models.CASCADE)
    border_frame = models.CharField(choices=BORDER_FRAME_CHOICES)
    color = models.CharField(max_length = 10, null = True, blank = True)
    usage_mode = models.CharField(choices=MODE_CHOICES)
    storage_code = models.CharField(max_length = 255, null = True, blank = True)
    document_expiration = models.CharField(choices=DOCUMENT_EXPIRATION_CHOICES)
    images_title = models.CharField(max_length = 255, null = True, blank = True)
    date = models.DateTimeField(default= timezone.datetime.now())
    physical_status = models.CharField(max_length = 255, null = True, blank = True)
    note = models.CharField(max_length = 255, null = True, blank = True)
    files = models.FileField(upload_to='files/',null = True, blank = True)
    info_additional = models.JSONField(blank=True,null=True,default=dict,editable=True,)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)

class Portfolio(Base):
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
    portfolio_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length = 255, null = True, blank = True)
    identification_code = models.CharField(max_length = 255, null = True, blank = True)
    classification_id = models.CharField(max_length = 255, null = True, blank = True)
    retention_period = models.CharField(max_length = 255, null = True, blank = True)
    usage_mode = models.CharField(choices=MODE_CHOICES)
    boxcase = models.ForeignKey(BoxCase,related_name='portfolio_boxcase',on_delete = models.CASCADE)
    physical_condition = models.CharField(max_length = 255, null = True, blank = True)
    key_word = models.CharField(max_length = 255, null = True, blank = True)
    annotation = models.CharField(max_length = 255, null = True, blank = True)
    barcode = models.CharField(max_length = 255, null = True, blank = True)
    usage_mode = models.CharField(choices=STATUS_CHOICES)
    start_date = models.DateTimeField(default = timezone.datetime.now())
    end_date = models.DateTimeField(default = timezone.datetime.now())
    # user = models.ForeignKey(User, on_delete=models.CASCADE)


class Watchlist(Base):
    watchlist_id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document,related_name='watchlist_document', on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder,related_name='watchlist_folder', on_delete=models.CASCADE)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    