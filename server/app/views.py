from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from .models import Employee,LeaveRequest
from .serializers import EmployeeSerializer,LeaverequestSerializer
from .permissions import isHRorOwnuser,isHR,isEmployee
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
# Create your views here.
User=get_user_model()

@api_view(['POST'])
def Register(request):
    if request.user.is_authenticated:
        return Response({"details":"Try Register after logout"},status=status.HTTP_302_FOUND)
    email = request.data.get('email', None)
    password = request.data.get('password', None)
    is_hr = request.data.get('is_hr', False)
    
    if not email or not password:
        return Response({'details': "Email and Password are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({"details": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(email=email, password=password, is_hr=is_hr)
    user.save()
    
    token= AccessToken.for_user(user)
    return Response({"details":"Registered Successfully","access_token":str(token)}, status=status.HTTP_201_CREATED)
@api_view(['POST'])
def Login(request):
    if request.user.is_authenticated:
        return Response({"details":"Try Login after logout"},status=status.HTTP_302_FOUND)
    email=request.data.get('email',None)
    password=request.data.get('password',None)
    if not email or not password:
        return Response({'details':"Email and Password are required"},status=status.HTTP_400_BAD_REQUEST)
    try:
        user=User.objects.get(email=email)
        if user.check_password(password):
            token=AccessToken.for_user(user)
            return Response({"access_token":str(token)},status=status.HTTP_200_OK)
        else:
            return Response({"details":"Password Invalid"},status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({"details":"User doesn't Exist"},status=status.HTTP_404_NOT_FOUND)

# class EmployeesAPIViewSet(ModelViewSet):
#     queryset = Employee.objects.all()
#     serializer_class = EmployeeSerializer
#     permission_classes = [IsAuthenticated, isHR]
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if not serializer.is_valid():
#             print(serializer.errors)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         user_email = serializer.validated_data['user']
#         try:
#             user = User.objects.get(email=user_email)
#         except User.DoesNotExist:
#             return Response({"details": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
#         if Employee.objects.filter(user=user).exists():
#             return Response({"details": "Employee with this user already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
#         employee = serializer.save(user=user)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated,isHR])
def EmployeeList(request):
    if request.method == 'POST':
        serializer = EmployeeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_email = serializer.validated_data['user']
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({"details": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        if Employee.objects.filter(user=user).exists():
            return Response({"details": "Employee with this user already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        employee = serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    employees = Employee.objects.all()
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated,isHRorOwnuser])
def EmployeeUpdateordelete(request, pk):
    try:
        employee = Employee.objects.get(pk=pk)
    except Employee.DoesNotExist:
        return Response({"details": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        leavestatus = request.data.get('status', None)
        if leavestatus and not request.user.is_hr:
            return Response({"details": "Only HR can update employee status"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        employee.delete()
        return Response({"details": "Employee deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    return Response(EmployeeSerializer(employee).data, status=status.HTTP_200_OK)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Employeeinfo(request):
    try:
        employee = Employee.objects.get(user__email=request.user.email)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Employee.DoesNotExist:
        return Response({"details": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
class LeaveRequestViewSet(ModelViewSet):
    # queryset = LeaveRequest.objects.all()
    serializer_class = LeaverequestSerializer
    permission_classes = [IsAuthenticated,isEmployee]
    def get_queryset(self):
        if self.request.user.is_hr:
            return LeaveRequest.objects.all()
        else:
            return LeaveRequest.objects.filter(employee__user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = Employee.objects.get(user=self.request.user)
        days= (serializer.validated_data['end_date'] - serializer.validated_data['start_date']).days + 1
        if days <= 0:
            return Response({"details": "Invalid date range"}, status=status.HTTP_400_BAD_REQUEST)
        if employee.leave_balance < days:
            return Response({"details": "Insufficient leave balance"}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.validated_data['start_date'] < employee.date_of_joining:
            return Response({"details": "Leave start date cannot be before date of joining"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(employee=employee, days=days)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def patch(self, request, *args, **kwargs):
        permission_classes= [isHRorOwnuser]
        pk= self.kwargs.get('pk')
        serializer = self.get_serializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        leave_request = LeaveRequest.objects.filter(pk=pk).first()
        if not leave_request:
            return Response({"details": "Leave request not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not request.user.is_hr and leave_request.employee.user != request.user:
            return Response({"details": "You do not have permission to update this leave request"}, status=status.HTTP_403_FORBIDDEN)
        leave_request = LeaveRequest.objects.get(pk=pk)
        if leave_request.status != 'Pending':
            return Response({"details": "Cannot update a request that is not pending"}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.validated_data.get('status') == 'Approved':
            leave_request.employee.leave_balance -= leave_request.days
            leave_request.employee.save()
        elif serializer.validated_data.get('status') == 'Rejected':
            leave_request.rejection_reason = serializer.validated_data.get('rejection_reason', '')
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        leave_request = LeaveRequest.objects.get(pk=pk)
        if leave_request.status != 'Pending':
            return Response({"details": "Cannot delete a request that is not pending"}, status=status.HTTP_400_BAD_REQUEST)
        leave_request.delete()
        return Response({"details": "Leave request deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        