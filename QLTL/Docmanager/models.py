from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Base(models.Model):
    UniqueID = models.AutoField(primary_key=True)
    is_visible = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Choices_status(models.TextChoices):
    wait = 'Chờ duyệt'
    finished = 'Hoàn thành'
    fail = 'Thất bại'

class Choices_policy(models.TextChoices):
    unlimited = 'Không hạn chế'
 
class Choices_frame(models.TextChoices):
    image = 'Hình ảnh'   

class Choices_expiration(models.TextChoices):
    vth = 'Vô thời hạn'
class WareHouse(models.Model):
    UniqueID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    warehouse_code = models.CharField(max_length=200)
class Shelf(models.Model):
    UniqueID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    warehouse_id = models.ForeignKey(WareHouse, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)

class BoxCase(models.Model):
    UniqueID = models.AutoField(primary_key=True)
    description = models.CharField(max_length=1000)
    name = models.CharField(max_length=200)
    shelf_id = models.ForeignKey(Shelf, on_delete=models.CASCADE)
    shelf_code = models.CharField(max_length=200)


class Folder(models.Model):
    UniqueID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    # folder_id = models.ForeignKey(Folder, on_delete=models.CASCADE)
    box_case_id = models.ForeignKey(BoxCase,  on_delete=models.CASCADE)
    shelf_id = models.ForeignKey(Shelf, on_delete=models.CASCADE)
    warehouse_id = models.ForeignKey(WareHouse, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=200)

class Portfolio(models.Model):
    UniqueID = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    identification_code = models.CharField(max_length=200)
    classification_id = models.CharField(max_length=200)
    retention_period = models.DateField()
    usage_policy = models.CharField(max_length=200, choices = Choices_policy )
    start_date = models.DateField()
    end_date = models.DateField()
    physical_condition = models.CharField(max_length=200)
    box_case_id = models.ForeignKey(BoxCase,  on_delete=models.CASCADE)
    keywords = models.CharField(max_length=200)
    annotation = models.CharField(max_length=200)
    barcode = models.CharField(max_length=200)
    status = models.CharField(max_length=100, choices = Choices_status)
    
class Document(models.Model):
    UniqueID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    portfolio_id = models.ForeignKey(Portfolio, blank=True, null=True, on_delete=models.CASCADE) 
    box_case_id = models.ForeignKey(BoxCase, on_delete=models.CASCADE)
    path = models.CharField(max_length=200)
    folder_id = models.ForeignKey(Folder, on_delete=models.CASCADE)
    border_frame = models.CharField(max_length=200, choices = Choices_frame )
    color = models.CharField(max_length=200)
    usage_mode = models.CharField(max_length=200, choices = Choices_policy )
    storage_code = models.CharField(max_length=100)
    document_expiration = models.CharField(max_length=200, choices = Choices_expiration)
    image_title = models.CharField(max_length=200)
    date = models.DateField()
    physical_status = models.CharField(max_length=200)
    note = models.CharField(max_length=1000)
    files = models.FileField(upload_to='images/')
    add_info = models.JSONField(null=True, blank=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    

class WatchList(models.Model):
    UniqueID = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, on_delete=models.CASCADE)
    folder_id = models.ForeignKey(Folder, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)









    
    
    
    

    
    
    
    
    
    
    
    
    
    