from rest_framework.permissions import BasePermission

from Docmanager.models import Document, Folder, Share
from django.contrib.auth.models import Group


# Check if the user belongs to a specific permission group?
def CheckGroupFactory(required_group):
    class CheckGroup(BasePermission):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.required_group = required_group

        def has_permission(self, request, view):
            if self.required_group:
                user_groups = request.user.groups.all()
                return user_groups.filter(name__in=required_group).exists()
                # return True
            else:
                return False  
    return CheckGroup

# Check the owner of a document or folder
def CheckOwnerFactory(Model):
    class CheckOwner(BasePermission):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
        
        def has_permission(self, request, view):
            try:
                id = view.kwargs.get('pk')
             
                if (int(id)):
                    getObject = Model.objects.get(id=id)
                    if getObject.owner == request.user:
                        return True 
                    else:
                        return False
            except ValueError:
                return False
            
    return CheckOwner

# Check if the folder is located within a shared folder or not?
def checkShare(folder_id, user, group):
    result = False
    folder = Folder.objects.get(id=folder_id)
    while True:
        share = Share.objects.filter(user=user, folder_id=folder.id, group = group)
        if share:
            result = True
            break
        elif folder.parent_folder is None:
            result = False
            break
        else:
            folder = folder.parent_folder
    return result

# Check if the document or folder is shared with the user with two permissions: only view and edit
def CheckSharedGroupdFactory(Model,groupname):
    class CheckOwner(BasePermission):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
        
        def has_permission(self, request, view):
            try:
                id = view.kwargs.get('pk')
                getObj=Model.objects.get(id=id)
                getGroup = Group.objects.get(name=groupname)
                
                shares = None
                if isinstance(getObj, Folder):
                    shares = Share.objects.filter(user=request.user, folder=getObj, group = getGroup)
                elif isinstance(getObj, Document):
                    shares = Share.objects.filter(user=request.user, document=getObj, group=getGroup)
                if shares:
                    return True
                return checkShare(getObj.id if isinstance(getObj, Folder) else getObj.folder.id,request.user,getGroup)
            except Exception:
                return False
    return CheckOwner


