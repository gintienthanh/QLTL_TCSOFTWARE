from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Base(models.Model):
    id = models.AutoField(primary_key=True)
    is_visibale = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
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

class Warehouse(Base):
    name = models.CharField(max_length = 255, null = True, blank = True)
    warehouse_code = models.CharField(max_length = 255, null = True, blank = True)
    
    def __str__(self) :
        return  self.name
   

class Shelf(Base):
    
    name = models.CharField(max_length = 255, null = True, blank = True)
    warehouse = models.ForeignKey(Warehouse,on_delete=models.CASCADE, null=True, blank=True)
    shelf_code = models.CharField(max_length = 255, null = True, blank = True)   
    
    def __str__(self) :
        return  self.name
    
class BoxCase(Base):
    description = models.CharField(max_length = 255)
    name = models.CharField(max_length = 255, null = True, blank = True)
    warehouse = models.ForeignKey(Warehouse,on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self) :
        return  self.name
   
    
class Portfolios(Base):
    
    title = models.CharField(max_length=200)
    identification_code = models.CharField(max_length=200)
    classification_id = models.CharField(max_length=200)
    retention_period = models.DateField(null=True, blank=True)
    usage_policy = models.CharField(max_length=200, )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    physical_condition = models.CharField(max_length=200)
    box_case = models.ForeignKey(BoxCase,  on_delete=models.CASCADE)
    keywords = models.CharField(max_length=200)
    annotation = models.CharField(max_length=200)
    barcode = models.CharField(max_length=200)
    status = models.CharField(max_length=100, choices = Choices_status)
    


class Folders(Base):
    name = models.CharField(max_length=200)
    box_case = models.ForeignKey(BoxCase,  on_delete=models.CASCADE)
    shelf = models.ForeignKey(Shelf,  on_delete=models.CASCADE)
    
    def __str__(self) :
        return  self.name

class Documents(Base):
    
    name = models.CharField(max_length=200)
    box_case = models.ForeignKey(BoxCase,  on_delete=models.CASCADE)
    path = models.CharField(max_length=200)
    folder = models.ForeignKey(Folders, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolios, on_delete=models.CASCADE)
    border_frame = models.CharField(max_length=200, choices = Choices_frame)
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
    folder = models.ForeignKey(Folders, on_delete=models.CASCADE)
    document = models.ForeignKey(Documents, on_delete=models.CASCADE)
    
    