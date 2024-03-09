from rest_framework.permissions import BasePermission

from Docmanager.models import Document, Folder, Share
from django.contrib.auth.models import Group


# Check if the user belongs to a specific permission group?
def checkGroupFactory(required_group):
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


# Check the owner of model
def CheckOwnerFactory(Model):
    class CheckOwner(BasePermission):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
        
        def has_permission(self, request, view):
            try:
                id = view.kwargs.get('pk')
                
                if(id):
                    getObject = type(Model).objects.get(id=id)
                    if getObject.owner == request.user:
                        return True 
                    else:
                        return False
            except ValueError:
                return False
            
    return CheckOwner

def checkShare(folder, user, type):
    folder_ids = Share.objects.filter(owner=user, type=type).values_list('folder_id', flat=True)

    while folder is not None:
        folder = Folder.objects.get(id=folder.id)
        if folder.id in folder_ids:
            return True
        folder = folder.parent_folder

    return False


# Check if the document or folder is shared with the user with two permissions: only view and edit
def CheckSharedGroupdFactory(Model, type):
    class CheckOwner(BasePermission):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def has_permission(self, request, view):
            try:
                id = view.kwargs.get('pk')
                if isinstance(Model, Folder):
                    obj = Model.objects.get(id=id)
                    if Share.objects.filter(owner=request.user, folder=obj, type=type).exists():
                        return True
                    if checkShare(obj, request.user, type):
                        return True
                    return False
                else:
                    if Share.objects.filter(owner=request.user, document=id, type=type).exists():
                        return True
                    return False
            except Exception:
                return False

    return CheckOwner