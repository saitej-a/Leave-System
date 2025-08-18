from .models import CustomUser, Employee, LeaveRequest
from rest_framework.serializers import ModelSerializer

# class CustomUserSerializer(ModelSerializer):
#     class Meta:
#         model=CustomUser
#         fields='__all__'
#         read_only_fields=['first_name','last_name','email']
class EmployeeSerializer(ModelSerializer):
    class Meta:
        model=Employee
        fields='__all__'
class LeaverequestSerializer(ModelSerializer):
    class Meta:
        model=LeaveRequest
        fields='__all__'
        read_only_fields=['employee','days','rejection_reason','status','created_at','updated_at']
