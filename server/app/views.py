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

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def EmployeeUpdateordelete(request, pk):
    
    try:
        employee = Employee.objects.get(pk=pk)
        if not request.user.is_hr and employee.user != request.user:
            return Response({"details": "You do not have permission to access this employee"}, status=status.HTTP_403_FORBIDDEN)
    except Employee.DoesNotExist:
        return Response({"details": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
    if (employee.user != request.user) and not ( request.user.is_hr) :
        return Response({"details": "You do not have permission to access this employee"}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'PATCH':
        if not request.user.is_hr:
            return Response({"details": "Only HR can update employee information"}, status=status.HTTP_403_FORBIDDEN)
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
    def partial_update(self, request, *args, **kwargs):
        record= self.get_object()
        if not record:
            return Response({"details": "Leave request not found"}, status=status.HTTP_404_NOT_FOUND)
        if record.status != 'Pending':
            return Response({"details": "Cannot update a leave request that is not pending"}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.is_hr :
            allowed_fields=['status', 'rejection_reason']
            data={ k:val for k,val in request.data.items() if k in allowed_fields}
            
            if data.get('status') == 'Approved':
                record.employee.leave_balance -= record.days if record.days else 0
                record.employee.save()
            elif data.get('status') == 'Rejected':
                record.rejection_reason = data.get('rejection_reason', '')
            else:
                return Response({"details": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
            record.status = data.get('status', record.status)
            record.save()
            serializer=self.get_serializer(record)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            if "status" in request.data:
                return Response({"details": "Employees cannot change status"}, 
                                status=status.HTTP_403_FORBIDDEN)

            serializer = self.get_serializer(record, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            days= (serializer.validated_data['end_date'] - serializer.validated_data['start_date']).days + 1
            if days <= 0:
                return Response({"details": "Invalid date range"}, status=status.HTTP_400_BAD_REQUEST)
            if record.employee.leave_balance < days:
                return Response({"details": "Insufficient leave balance"}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.validated_data['start_date'] < record.employee.date_of_joining:
                return Response({"details": "Leave start date cannot be before date of joining"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(days=days)
            return Response(serializer.data, status=status.HTTP_200_OK)
    def destroy(self, request, *args, **kwargs):
        try:
            record = self.get_object()
        except LeaveRequest.DoesNotExist:
            return Response({"details": "Leave request not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user.is_hr or record.employee.user == request.user:
            if record.status != 'Pending':
                return Response({"details": "Cannot delete a leave request that is not pending"},
                                status=status.HTTP_400_BAD_REQUEST)
            record.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"details": "You do not have permission to delete this leave request"},
                        status=status.HTTP_403_FORBIDDEN)
