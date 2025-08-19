# 🗂️ Mini Leave Management System (Django + DRF + JWT)

A simple **Leave Management System** built with **Django REST Framework** and **JWT authentication**, designed for small organizations.  
This system allows **HR** to manage employees and leave requests, while **Employees** can apply, update, and track their leaves.  

---

## 🚀 Features

### 🔑 Authentication
- User **Register/Login** with JWT tokens.
- Role-based users (`HR` or `Employee`).

### 👨‍💼 HR Capabilities
- Add new employees.
- View, update, and delete employee records.
- View all leave requests.
- Approve or reject leave requests.
- Manage leave balances.

### 👨‍💻 Employee Capabilities
- View own profile and leave balance.
- Apply for leave.
- Update or cancel leave requests (if still pending).
- View request status (Approved/Rejected/Pending).

### ✅ Edge Cases Handled
- Applying leave **before joining date**.
- Leave requests exceeding **available balance**.
- **End date before start date**.
- Overlapping or invalid leave requests.
- Unauthorized access to other users’ data.
- Prevent modification/deletion of **non-pending** leave requests.

---

## 🛠️ Tech Stack
- **Backend**: Django, Django REST Framework  
- **Authentication**: JWT (SimpleJWT)  
- **Database**: SQLite (dev) / PostgreSQL or MySQL (prod)  
- **API Testing**: Postman / cURL  

---

## 📂 Project Structure
```
project/
│── app/
│   ├── views.py
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── urls.py
│── manage.py
│── requirements.txt
│── README.md
```

---

## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/saitej-a/Leave-System.git
   cd Leave-System/server/

   ```

2. **Create virtual environment & activate**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

6. **Test APIs** using Postman or cURL.  

---

## 🔗 API Endpoints

### Authentication
- `POST /auth/register/` → Register new user  
- `POST /auth/login/` → Login and get access token  

### Employee Management
- `GET /employees/` → List all employees (HR only)  
- `POST /employees/` → Add employee (HR only)  
- `GET /employees/me/` → Get logged-in employee info  
- `GET /employees/{id}/` → Get employee by ID (HR or self)  
- `PATCH /employees/{id}/` → Update employee (HR only)  
- `DELETE /employees/{id}/` → Delete employee (HR only)  

### Leave Management
- `GET /leaverequests/` → List leave requests (HR → all, Employee → own)  
- `POST /leaverequests/` → Apply for leave (Employee only)  
- `PATCH /leaverequests/{id}/` → Update leave request  
   - HR → Approve/Reject  
   - Employee → Update dates if pending  
- `DELETE /leaverequests/{id}/` → Delete leave request (HR or self if pending)  

---

## 🖼️ Architecture
```plaintext
Frontend (Client) → API Endpoints → Django REST Framework (Backend) → Database
```
- **Frontend (optional)**: React / Angular / Mobile app.  
- **Backend**: Django REST Framework + JWT for auth.  
- **Database**: Stores users, employees, leave requests.  

---

## 🚧 Future Improvements
- Notifications (email/SMS on leave approval/rejection).  

---

## 🌍 Deployment
- The backend is deployed on PythonAnywhere.
    - Base URL: https://symploratest.pythonanywhere.com/api/
    - Admin Credentials:
        Email: ankamsaiteja27@gmail.com
        Password: 123
---

## 🙌 Acknowledgments
Thanks to Django & DRF community for their documentation and tutorials.  

---


