from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,Group

# from Docmanager.models import Document, Folder

class UserManager(BaseUserManager):
    def create_user(self,email,username=None,password=None,password2=None):
        if not email:
            raise ValueError('User must have an email Address!')
        user = self.model(
            email = self.normalize_email(email), 
        ) 
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,username=None,password=None):
        user = self.create_user(
          email,
          password=password,
          username=username
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google',
                  'twitter': 'twitter', 'email': 'email'}
class User(AbstractBaseUser):
    email = models.EmailField(
      verbose_name='Email',
      max_length=255,
      unique=True,
    )
    username = models.CharField(max_length=200,blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('email'))
    # sử dụng để cho phép quản lý các người dùng
    objects = UserManager()
    USERNAME_FIELD = 'email'
    def __str__(self):
      return self.email
    def has_perm(self, perm, obj=None):
      "Does the user have a specific permission?"
      # setting base on request : để check quyền "perm " được nhận vào
      # ở đây set lập sẵn là is_admin sau có thế sửa lai
      return self.is_admin
    def has_module_perms(self, app_label):
      "Does the user have permissions to view the app `app_label`?"
      # Simplest possible answer: Yes, always
      return True
    @property
    def is_staff(self):
      "Is the user a member of staff?"
      # Simplest possible answer: All admins are staff
      return self.is_admin