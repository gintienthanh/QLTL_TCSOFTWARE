from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import Group
from django.utils import timezone
from enum import Enum

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length = 12)
class Base(models.Model):
    id = models.AutoField(primary_key=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    delete_at = models.DateTimeField(auto_now=False,null=True)
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    create_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='%(class)s_created')
    delete_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='%(class)s_deleted')
    editor = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='%(class)s_editor')
    class  Meta:
        abstract = True
    
    def soft_delete(self, request):
        self.is_delete = True
        self.delete_at = timezone.now()
        self.delete_by = request.user
        self.save()
    
    
class ChoicesStatus(Enum):
    wait = 'Wait'
    finished = 'Finished'
    fail = 'Fail'
    
    
class ChoicesFrame(Enum):
    img = 'img'
    txt = 'txt'
   
    
class ChoicesTypeWarehouse(Enum):
    BoxCase = 'boxcase'
    Warehouse = 'warehouse'
    Shelf = 'shelf'

class ChoicesType(Enum):
    File = 'File'
    Folder = 'Folder'

class ChoicesSharingType(Enum):
    ONLY_VIEW = 'only_view'
    EDIT = 'edit'


class Warehouse(Base):

    name = models.CharField(max_length = 255, null = True)
    code = models.CharField(max_length = 255, null = True)
    description = models.CharField(max_length = 255, null = True)
    type_warehouse = models.CharField(max_length=100, choices=[(tag.value, tag.name) for tag in ChoicesTypeWarehouse], default=ChoicesTypeWarehouse.Warehouse.value)
    parent_warehouse = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='subwarehouse') 
    def __str__(self) :
        return  self.name
    
class ClassifyVariant(models.Model):
    variant_name = models.CharField(max_length=100)
    def __str__(self) :
        return  self.variant_name
    
class RetentionPeriod(Base):
    
    name = models.CharField(max_length=200, null = True)
    description = models.CharField(max_length=1000, null = True)
    def __str__(self):
        return self.name
class Language(Base):
    name = models.CharField(max_length=200, null = True )
    description = models.CharField(max_length=1000, null = True)
    def __str__(self):
        return self.name

  
class Portfolio(Base):
    
    title = models.CharField(max_length=200, null=True)
    identification_code = models.CharField(max_length=200, null=True)
    classification = models.ForeignKey(ClassifyVariant, null = True, on_delete=models.CASCADE)
    retention_period = models.ForeignKey(RetentionPeriod, null=True, on_delete=models.CASCADE)
    usage_policy = models.CharField(max_length=200, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    physical_condition = models.CharField(max_length=200, null=True)
    warehouse = models.ForeignKey(Warehouse,null=True,  on_delete=models.CASCADE)
    keywords = models.CharField(max_length=200, null=True)
    annotation = models.CharField(max_length=200, null=True)
    barcode = models.CharField(max_length=200, null=True)
    languege = models.ForeignKey(Language, null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=[(tag.value, tag.name) for tag in ChoicesStatus], default=ChoicesStatus.wait.value)

class Folder(Base):
    name = models.CharField(max_length=255)
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='subfolders') 
    path = models.CharField(max_length=255, null=True)
    files = models.FileField(upload_to='files/',null=True)
    file_size = models.BigIntegerField(null=True)
    type = models.CharField(max_length=100, choices=[(tag.value, tag.name) for tag in ChoicesType], default=ChoicesType.Folder.value)
    
    def __str__(self) :
        return  self.name

class Document(Base):
    
    name = models.CharField(max_length=200)
    box_case = models.ForeignKey(Warehouse,  on_delete=models.CASCADE, null = True)
    path = models.CharField(max_length=200,null=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE,  null = True)
    border_frame = models.CharField(max_length=200, choices=[(tag.value, tag.name) for tag in ChoicesFrame], default=ChoicesFrame.img.value)
    color = models.CharField(max_length=200,null=True)
    usage_mode = models.CharField(max_length=200,null=True)
    storage_code = models.CharField(max_length=100,null=True)
    document_expiration = models.CharField(max_length=200,null=True)
    image_title = models.CharField(max_length=200,null=True)
    date = models.DateField(null = True)
    physical_status = models.CharField(max_length=200,null=True)
    note = models.CharField(max_length=1000,null=True)
    files = models.FileField(upload_to='files/', null=True)
    type = models.CharField(max_length=100, choices=[(tag.value, tag.name) for tag in ChoicesType], default=ChoicesType.Folder.value)
    add_info = models.JSONField(null=True)

    def __str__(self) :
        return  self.name
    
    
class Watchlist(Base): 
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE , null=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE , null=True)

class Share(Base):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=100, choices=[(tag.value, tag.name) for tag in ChoicesSharingType], default=ChoicesSharingType.ONLY_VIEW.value )
    
