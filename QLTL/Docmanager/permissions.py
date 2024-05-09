from rest_framework.permissions import BasePermission

from Docmanager.models import Document, Folder, Share
from django.contrib.auth.models import Group,Permission


# Check if the user belongs to a specific permission group?
def check_group_factory(required_group):
    class CheckGroup(BasePermission):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.required_group = required_group

        def has_permission(self, request, view):
            try:
                if self.required_group:
                    group = Group.objects.filter(name=required_group).first()
                    user_groups = request.user.groups.all()
                    return user_groups.filter(name=group.name).exists()
                    # return True
                else:
                    return False  
            except Exception:
                return False
    
    return CheckGroup

def check_group_permisison_factory(Model):
    class CheckGroupPermission(BasePermission):
        def __init__(self, *args, **kwargs):
            super().__init__()
        def has_permission(self,request,view):
            try:
                http_method = request.method
                permission_type = ''
                if http_method == 'GET':
                    permission_type = f'view_{Model}'
                if http_method == 'POST':
                    permission_type = f'add_{Model}'
                if http_method == 'PUT' or http_method == 'PATCH':
                    permission_type = f'change_{Model}'
                if http_method == 'DELETE':
                    permission_type = f'delete_{Model}'
                permission = Permission.objects.get(codename = permission_type)
                permisison_groups = Group.objects.filter(permissions = permission.pk)
                user_groups = Group.objects.filter(user = request.user)
                intersection = set(permisison_groups) & set(user_groups)
                if intersection:
                    return True
                return False

            except Exception:
                return False
    return CheckGroupPermission

# Check the owner of model
def Check_owner_factory(Model):
    class CheckOwner(BasePermission):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
        
        def has_permission(self, request, view):
            try:
                http_method = request.method
                if http_method in ['PUT', 'PATCH', 'DELETE']:
                    id = view.kwargs.get('pk')
                    if(id):
                        obj = type(Model).objects.get(id=id)
                        if obj.owner == request.user:
                            return True 
                        else:
                            return False
                # list_object =  type(Model).object.get(owner = request.user)
                # if list_object:
                #     return True
                # return False
            except ValueError:
                return False
            
    return CheckOwner

def Check_owner_parent_factory(Model,parent):
    class CheckOwnerParent(BasePermission):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
        
        def has_permission(self, request, view):
            try:
                http_method = request.method
                if http_method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                    id = view.kwargs.get('pk')
                    data = request.data.copy()
                    if http_method == 'POST':
                        id = data.get(parent)
                    if(id):
                        obj = type(Model).objects.get(id=id)
                        print(obj.owner)
                        print(request.user)
                        if obj.owner == request.user:
                            return True 
                        else:
                            return False
                # list_object =  type(Model).object.get(owner = request.user)
                # if list_object:
                #     return True
                # return False
            except ValueError:
                return False
            
    return CheckOwnerParent
def checkShare(folder, user, type):
    folder_ids = Share.objects.filter(owner=user, type=type).values_list('folder_id', flat=True)

    while folder is not None:
        folder = Folder.objects.get(id=folder.id)
        if folder.id in folder_ids:
            return True
        folder = folder.parent_folder

    return False


# Check if the document or folder is shared with the user with two permissions: only view and edit
def check_shared_group_factory(Model, type):
    class CheckOwner(BasePermission):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def has_permission(self, request, view):
            try:
                http_method = request.method
                id = view.kwargs.get('pk',None)
                if http_method == 'GET':
                    return True
                if isinstance(Model, Folder):
                    if not id:
                        data = request.data.copy()
                        if http_method == 'POST':
                            id = data.get('parent_folder')
                        if not id:
                            return True
                    obj = Folder.objects.get(id=id)
                    if Share.objects.filter(owner=request.user, folder=obj, type=type).exists():
                        return True
                    if checkShare(obj, request.user, type):
                        return True
                    return False
                else:
                    if Share.objects.filter(owner=request.user, document=id, type=type).exists():
                        return True
                    return False
                
            except Exception as e:
                return False
    return CheckOwner