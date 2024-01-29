from django.db import models

# Create your models here.
class Base(models.Models):
    base_id = models.AutoField(primary_key=True)
    is_visibale = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Choices_status(models.TextChoices):
    wait = 'Chờ duyệt'
    finished = 'Hoàn thành'
    fail = 'Thất bại'


class Warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length = 255, null = True, blank = True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    warehouse_code = models.CharField(max_length = 255, null = True, blank = True)

class Shelf(models.Model):
    shelf_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length = 255, null = True, blank = True)
    warehouse_id = models.ForeignKey(Warehouse,on_delete=models.CASCADE, null=True, blank=True)

class BoxCase(models.Model):
    box_case_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length = 255)
    name = models.CharField(max_length = 255, null = True, blank = True)
    warehouse_id = models.ForeignKey(Warehouse,on_delete=models.CASCADE, null=True, blank=True)
    shelf_code = models.CharField(max_length = 255, null = True, blank = True)   
    
    
class Portfolios(models.Model):
    portfolio_id = models.AutoField(primary_key=True)
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
    
class Documents(models.Model):
    document_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    box_case_id = models.ForeignKey(BoxCase,  on_delete=models.CASCADE)
    path = models.CharField(max_length=200)
    foder_id = models.ForeignKey(Foder, on_delete=models.CASCADE)
    border_frame = models.CharField(max_length=200, choises = Choices_frame )
    color = models.CharField(max_length=200)
    usage_mode = models.CharField(max_length=200, choices = Choices_usage)
    storage_code = models.CharField(max_length=100)
    document_expiration = models.CharField(max_length=200, choices = Choices_expiration)
    image_title = models.CharField(max_length=200)
    date = models.DateField()
    physical_status = models.CharField(max_length=200)
    note = models.CharField(max_length=1000)
    files = models.FileField(upload_to='images/')
    add_info = models.JSONField(null=True, blank=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)

