from Auth.models import User
from django.db import models
from django.contrib.auth.models import Group


# Create your models here.
class Base(models.Model):
    id = models.AutoField(primary_key=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    create_by = models.ForeignKey(User,  related_name='%(class)s_created')
    delete_by = models.ForeignKey(User,  related_name='%(class)s_deleted')
    class  Meta:
        abstract = True
       
    
    
class Choices_status(models.TextChoices):
    wait = 'Chờ duyệt'
    finished = 'Hoàn thành'
    fail = 'Thất bại'
    
    
class Choices_frame(models.TextChoices):
    img = 'hình ảnh'
    txt = 'văn bản'
    page = 'khung biên trang'
    
class Choices_type_warehouse(models.TextChoices):
    BoxCase = 'Hộp cặp'
    Warehouse = 'Kho'
    Shelf = 'Giá Kệ'

class Choices_type(models.TextChoices):
    File = 'File'
    Folder = 'Folder'




class Warehouse(Base):
    name = models.CharField(max_length = 255, null = True, blank = True)
    code = models.CharField(max_length = 255, null = True, blank = True)
    description = models.CharField(max_length = 255)
    type_warehouse = models.CharField(max_length=100, choices = Choices_type_warehouse.choices)
    def __str__(self) :
        return  self.name
    
class Portfolio(Base):
    
    title = models.CharField(max_length=200)
    identification_code = models.CharField(max_length=200)
    classification_id = models.CharField(max_length=200)
    retention_period = models.DateField(null=True, blank=True)
    usage_policy = models.CharField(max_length=200, )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    physical_condition = models.CharField(max_length=200)
    box_case = models.ForeignKey(Warehouse,  on_delete=models.CASCADE)
    keywords = models.CharField(max_length=200)
    annotation = models.CharField(max_length=200)
    barcode = models.CharField(max_length=200)
    status = models.CharField(max_length=100, choices = Choices_status.choices)
    


class Folder(Base):
    name = models.CharField(max_length=200)
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders') 
    path = models.CharField(max_length=255, null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=100, choices = Choices_type.choices)
    
    def __str__(self) :
        return  self.name

class Document(Base):
    
    name = models.CharField(max_length=200)
    box_case = models.ForeignKey(Warehouse,  on_delete=models.CASCADE)
    path = models.CharField(max_length=200)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    border_frame = models.CharField(max_length=200, choices = Choices_frame.choices)
    color = models.CharField(max_length=200)
    usage_mode = models.CharField(max_length=200)
    storage_code = models.CharField(max_length=100)
    document_expiration = models.CharField(max_length=200)
    image_title = models.CharField(max_length=200)
    date = models.DateField(null = True, blank = True)
    physical_status = models.CharField(max_length=200)
    note = models.CharField(max_length=1000)
    files = models.FileField(upload_to='files/')
    add_info = models.JSONField(null=True, blank=True)
    
    def __str__(self) :
        return  self.name
    
    
class Watchlist(Base): 
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE , null=True, blank=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE , null=True, blank=True)

class Share(Base):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='shared_user')
    
    