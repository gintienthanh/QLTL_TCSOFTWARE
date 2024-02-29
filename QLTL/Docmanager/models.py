from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import Group
from enum import Enum

# Create your models here.
class Base(models.Model):
    id = models.AutoField(primary_key=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    delete_at = models.DateTimeField(auto_now=False,null=True, blank=True)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    create_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='%(class)s_created')
    delete_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='%(class)s_deleted')
    editor = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='%(class)s_editor')
    class  Meta:
        abstract = True
       
    
    
class Choices_status(Enum):
    wait = 'Wait'
    finished = 'Finished'
    fail = 'Fail'
    
    
class Choices_frame(Enum):
    img = 'img'
    txt = 'txt'
   
    
class Choices_type_warehouse(Enum):
    BoxCase = 'boxcase'
    Warehouse = 'warehouse'
    Shelf = 'shelf'

class Choices_type(Enum):
    File = 'File'
    Folder = 'Folder'

class ChoicesSharingType(Enum):
    ONLY_VIEW = 'only_view'
    EDIT = 'edit'


class Warehouse(Base):

    name = models.CharField(max_length = 255, null = True, blank = True)
    code = models.CharField(max_length = 255, null = True, blank = True)
    description = models.CharField(max_length = 255, null = True, blank = True)
    type_warehouse = models.CharField(max_length=100, choices=[(tag.value, tag.name) for tag in Choices_type_warehouse], default=Choices_type_warehouse.Warehouse.value)
    parent_warehouse = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subwarehouse') 
    def __str__(self) :
        return  self.name
    
class ClassifyVariant(models.Model):
    variant_name = models.CharField(max_length=100)
    def __str__(self) :
        return  self.variant_name
    

  
class Portfolio(Base):
    
    title = models.CharField(max_length=200, null=True, blank=True)
    identification_code = models.CharField(max_length=200, null=True, blank=True)
    classification = models. ForeignKey(ClassifyVariant, blank=True, null = True, on_delete=models.PROTECT)
    retention_period = models.DateField(null=True, blank=True)
    usage_policy = models.CharField(max_length=200, null=True, blank=True )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    physical_condition = models.CharField(max_length=200, null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse,null=True, blank=True,  on_delete=models.CASCADE)
    keywords = models.CharField(max_length=200, null=True, blank=True)
    annotation = models.CharField(max_length=200, null=True, blank=True)
    barcode = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=100, choices=[(tag.value, tag.name) for tag in Choices_status], default=Choices_status.wait.value)
    


class Folder(Base):
    name = models.CharField(max_length=255)
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders') 
    path = models.CharField(max_length=255, null=True, blank=True)
    files = models.FileField(upload_to='files/',null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    type = models.CharField(max_length=100, choices=[(tag.value, tag.name) for tag in Choices_type], default=Choices_type.Folder.value)
    
    def __str__(self) :
        return  self.name

class Document(Base):
    
    name = models.CharField(max_length=200)
    box_case = models.ForeignKey(Warehouse,  on_delete=models.CASCADE, null = True, blank = True)
    path = models.CharField(max_length=200,null=True, blank=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE,  null = True, blank = True)
    border_frame = models.CharField(max_length=200, choices=[(tag.value, tag.name) for tag in Choices_frame], default=Choices_frame.img.value)
    color = models.CharField(max_length=200,null=True, blank=True)
    usage_mode = models.CharField(max_length=200,null=True, blank=True)
    storage_code = models.CharField(max_length=100,null=True, blank=True)
    document_expiration = models.CharField(max_length=200,null=True, blank=True)
    image_title = models.CharField(max_length=200,null=True, blank=True)
    date = models.DateField(null = True, blank = True)
    physical_status = models.CharField(max_length=200,null=True, blank=True)
    note = models.CharField(max_length=1000,null=True, blank=True)
    files = models.FileField(upload_to='files/', null=True, blank=True)
    type = models.CharField(max_length=100, choices=[(tag.value, tag.name) for tag in Choices_type], default=Choices_type.Folder.value)
    add_info = models.JSONField(null=True, blank=True)
    
    def __str__(self) :
        return  self.name
    
    
class Watchlist(Base): 
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE , null=True, blank=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE , null=True, blank=True)

class Share(Base):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=100, choices=[(tag.value, tag.name) for tag in ChoicesSharingType], default=ChoicesSharingType.ONLY_VIEW.value )
    
    