from django.urls import path, include
from .views import Login, LeaveRequestViewSet, Register, Employeeinfo,EmployeeList,EmployeeUpdateordelete
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'leaverequests', LeaveRequestViewSet, basename='leaverequest')
# router.register(r'employees', EmployeesAPIViewSet, basename='employee')
urlpatterns = [
    path('auth/login/',Login),
    path('auth/register/',Register),
    path('employees/', EmployeeList, name='employee_list'),path('employees/me/',Employeeinfo, name='employee_info'),
    path('employees/<int:pk>/', EmployeeUpdateordelete, name='employee_update_or_delete'),
    
    path('', include(router.urls)),
]
