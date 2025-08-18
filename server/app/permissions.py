from rest_framework.permissions import BasePermission
from .models import LeaveRequest,Employee
class isHRorOwnuser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_hr:
            return True
        return request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        # print("Checking permissions for:", obj)
        if request.user.is_hr:
            return True
        # print("User is not HR, checking if it's own user")
        if isinstance(obj, LeaveRequest):
            return obj.employee.user == request.user
        # print("Checking for Employee object")
        if isinstance(obj, Employee):
            # print(obj.user==request.user)
            return obj.user == request.user
        # print("Object is neither LeaveRequest nor Employee")
        return False
        
class isHR(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_hr:
            return True
        return False
class isEmployee(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated :
            user= request.user
            if Employee.objects.filter(user=user).exists():
                return True
            
        return False