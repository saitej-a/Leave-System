import requests as re
import json
# token=re.post('http://127.0.0.1:8000/api/auth/login/',data={
#     'email':'ankamsaiteja27@gmail.com',
#     'password':'123'})
# token=token.json()
# acc_token=token['access_token']
# with open('token.txt', 'w') as f:
#     f.write(acc_token)
token = open('token.txt', 'r')
acc_token = token.read()
headers = {
    'Content-Type': 'application/json',
    'Authorization':f'Bearer {acc_token}'
}
data={
    # 'user': 'ankamsaiteja27+123@gmail.com',
    # 'department': 'IT',
    # 'position': 'Software Engineer',
    # 'date_of_joining': '2023-10-01',
    'leave_balance': 20
}
data2={'start_date': '2025-08-18', 'end_date': '2025-08-20', 'reason': 'Vacation'}
data3={'status': 'Approved', 'rejection_reason': 'Not applicable'}
response = re.patch('http://127.0.0.1:8000/api/leaverequests/1/',headers=headers,data=json.dumps(data3))
# response=re.patch('http://127.0.0.1:8000/api/employees/1/',headers=headers,data=json.dumps(data))
print(response.json())
# ,data=json.dumps({"status": "Approved"})