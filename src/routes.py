from flask import Blueprint, jsonify, request
from src.models import db, User, Employee, PasswordResetToken, Payroll, Attendance
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from src.send_email import send_email
from hashlib import sha256
import os
from datetime import datetime, timezone, timedelta

api = Blueprint('api', __name__)

@api.route("/hello", methods=["GET"])
def index():
    return jsonify(message="Welcome to PayTrack API v1.0!")

@api.route("/admin/register", methods=["POST"])
def regisster_admin():
    request_body = request.get_json()

    secret_key = request_body.get("secret_key")
    
    if secret_key != os.getenv("JWT_SECRET_KEY"):
        return jsonify(message="Invalid secret key"), 401
        
    email = request_body.get("email")
    password = request_body.get("password")
    
    password_hash = sha256(password.encode()).hexdigest()
    
    user = User(email=email, password_hash=password_hash, role="admin")
    db.session.add(user)
    db.session.commit()
    
    return jsonify(message="Admin user created successfully!")


@api.route("/employee/register", methods=["POST"])
@jwt_required()
def register_employee():
    token = PasswordResetToken.query.filter_by(employee_id=get_jwt_identity()).first()
    
    if token.expires_at.tzinfo is None:
        token.expires_at = token.expires_at.replace(tzinfo=timezone.utc)
    
    if token is None or token.used or token.expires_at < datetime.now(tz=timezone.utc):
        return jsonify(message="Invalid or expired token"), 400
        
    token.used = True

    db.session.commit()
    
    request_body = request.get_json()
    
    email = request_body.get("email")
    password = request_body.get("password")
    security_question_1 = request_body.get("security_question_1")
    security_answer_1 = request_body.get("security_answer_1")
    
    if not email or not password or not security_question_1 or not security_answer_1:
        return jsonify(message="All fields are required"), 400
    
    password_hash = sha256(password.encode()).hexdigest()
    
    user = User(email=email, password_hash=password_hash, security_question_1=security_question_1, security_answer_1=security_answer_1, role="employee")
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    
    employee = Employee.query.get(get_jwt_identity())
    employee.user_id = user.user_id
    
    return jsonify(message="Employee user created successfully!")

@api.route("/login", methods=["POST"])
def login_admin():
    request_body = request.get_json()
    
    email = request_body.get("email")
    password = request_body.get("password")
    
    password_hash = sha256(password.encode()).hexdigest()
    
    user = User.query.filter_by(email=email, password_hash=password_hash).first()
    
    if user is None:
        return jsonify(message="Invalid email or password"), 401
        
    access_token = create_access_token(identity=user.user_id, additional_claims={"role": user.role})
    
    return jsonify(access_token=access_token)

@api.route("/manage/employee", methods=["GET"])
@jwt_required()
def get_employees():
    current_user_id = get_jwt_identity()
    
    user = User.query.get(current_user_id)
    
    if user.role != "admin":
        return jsonify(message="You are not authorized to perform this action"), 403
        
    employees = Employee.query.all()
    
    return jsonify([employee.serialize() for employee in employees])

@api.route("/manage/employee/add", methods=["POST"])
@jwt_required()
def add_employee():
    current_user_id = get_jwt_identity()
    
    user = User.query.get(current_user_id)
    
    if user.role != "admin":
        return jsonify(message="You are not authorized to perform this action"), 403
        
    request_body = request.get_json()
    
    email = request_body.get("email")
    
    employee = Employee.query.filter_by(personal_email=email).first()
    
    if employee is not None:
        return jsonify(message="Employee with this email already exists"), 400
    
    first_name = request_body.get("first_name")
    last_name = request_body.get("last_name")
    address = request_body.get("address")
    phone = request_body.get("phone")
    position = request_body.get("position")
    department = request_body.get("department")
    start_date = request_body.get("start_date")
    
    employee = Employee(personal_email=email,first_name=first_name, last_name=last_name, address=address, phone=phone, position=position, department=department, start_date=start_date)
    db.session.add(employee)
    db.session.commit()
    db.session.refresh(employee)
    
    password_reset_token = create_access_token(identity=employee.employee_id)
    
    token = PasswordResetToken(employee_id=employee.employee_id, token=password_reset_token, expires_at=datetime.now(tz=timezone.utc) + timedelta(hours=24))
    
    db.session.add(token)
    db.session.commit()
    
    send_email(url=f"{os.getenv('FRONT_URL')}/employee/register?token={password_reset_token}", name=f"{first_name} {last_name}", recipient=email)
    
    
    return jsonify(message="Employee added successfully!"), 201

@api.route("/manage/employee/<int:employee_id>", methods=["GET"])
@jwt_required()
def get_employee(employee_id):
    current_user_id = get_jwt_identity()
    
    user = User.query.get(current_user_id)
    
    if user.role != "admin":
        return jsonify(message="You are not authorized to perform this action"), 403
        
    employee = Employee.query.get(employee_id)
    
    if employee is None:
        return jsonify(message="Employee not found"), 404
        
    return jsonify(employee.serialize())

@api.route("/manage/employee/<int:employee_id>", methods=["PUT"])
@jwt_required()
def update_employee(employee_id):
    current_user_id = get_jwt_identity()
    
    user = User.query.get(current_user_id)
    
    if user.role != "admin":
        return jsonify(message="You are not authorized to perform this action"), 403
        
    employee = Employee.query.get(employee_id)
    
    if employee is None:
        return jsonify(message="Employee not found"), 404
        
    request_body = request.get_json()
    
    email = request_body.get("email")
    
    if email:
        employee.personal_email = email
    
    first_name = request_body.get("first_name")
    
    if first_name:
        employee.first_name = first_name
    
    last_name = request_body.get("last_name")
    
    if last_name:
        employee.last_name = last_name
    
    address = request_body.get("address")
    
    if address:
        employee.address = address
    
    phone = request_body.get("phone")
    
    if phone:
        employee.phone = phone
    
    position = request_body.get("position")
    
    if position:
        employee.position = position
    
    department = request_body.get("department")
    
    if department:
        employee.department = department
    
    start_date = request_body.get("start_date")
    
    if start_date:
        employee.start_date = start_date
    
    db.session.commit()
    
    return jsonify(message="Employee updated successfully!")


@api.route("/manage/employee/<int:employee_id>", methods=["DELETE"])
@jwt_required()
def delete_employee(employee_id):
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)

    if user.role != "admin":
        return jsonify(message="You are not authorized to perform this action"), 403

    employee = Employee.query.get(employee_id)

    if employee is None:
        return jsonify(message="Employee not found"), 404

    employee_user = User.query.get(employee.user_id)

    try:
        if employee_user:
            db.session.delete(employee_user)

        db.session.delete(employee)
        db.session.commit()

        return jsonify(message="Employee deleted successfully!")
    except Exception as e:
        db.session.rollback()
        return jsonify(message=f"Failed to delete employee: {str(e)}"), 500

@api.route("/employee/password-reset", methods=["POST"])
def password_reset_request():
    request_body = request.get_json()
    
    email = request_body.get("email")
    
    user = User.query.filter_by(email=email).first()
    
    if user is None:
        return jsonify(message="User not found"), 404
        
    employee = Employee.query.filter_by(user_id=user.user_id).first()
    
    if employee is None:
        return jsonify(message="Employee not found"), 404
        
    password_reset_token = create_access_token(identity=employee.employee_id)
    
    token = PasswordResetToken(employee_id=employee.employee_id, token=password_reset_token, expires_at=datetime.now(tz=timezone.utc) + timedelta(hours=24))
    
    db.session.add(token)
    db.session.commit()
    
    send_email(url=f"{os.getenv('FRONT_URL')}/employee/password-reset?token={password_reset_token}", name=f"{employee.first_name} {employee.last_name}", recipient=email)
    
    return jsonify(message="Password reset link sent successfully!")

@api.route("/employee/password-reset/<string:token>", methods=["POST"])
def password_reset(token):
    password_reset_token = PasswordResetToken.query.filter_by(token=token).first()
    
    if password_reset_token is None or password_reset_token.used or password_reset_token.expires_at < datetime.now(tz=timezone.utc):
        return jsonify(message="Invalid or expired token"), 400
        
    request_body = request.get_json()
    
    password = request_body.get("password")
    
    security_question_1 = request_body.get("security_question_1")
    email = request_body.get("email")
    
    user = User.query.get(password_reset_token.user_id)
    
    if user.security_question_1 != security_question_1:
        return jsonify(message="Invalid security answer"), 400
    
    if user.email != email:
        return jsonify(message="Invalid email"), 400

    
    password_hash = sha256(password.encode()).hexdigest()
    
    user = User.query.get(password_reset_token.employee_id)
    
    user.password_hash = password_hash
    
    password_reset_token.used = True
    
    db.session.commit()
    
    return jsonify(message="Password reset successfully!")

@api.route("/admin/employee/<int:employee_id>/payroll/create", methods=["POST"])
@jwt_required()
def create_payroll(employee_id):
    current_user_id = get_jwt_identity()
    
    user = User.query.get(current_user_id)
    
    if user.role != "admin":
        return jsonify(message="You are not authorized to perform this action"), 403
        
    employee = Employee.query.get(employee_id)
    
    if employee is None:
        return jsonify(message="Employee not found"), 404
        
    request_body = request.get_json()
    
    pay_date = request_body.get("pay_date")
    hours_worked = request_body.get("hours_worked")
    hourly_rate = request_body.get("hourly_rate")
    tax_deduction = request_body.get("tax_deduction")
    gross_salary = hours_worked * hourly_rate
    net_salary = gross_salary - tax_deduction
    
    new_payroll = Payroll(employee_id=employee_id, pay_date=pay_date, hours_worked=hours_worked,
                          hourly_rate=hourly_rate, tax_deduction=tax_deduction, gross_salary=gross_salary, net_salary=net_salary)
    
    db.session.add(new_payroll)
    db.session.commit()
    
    return jsonify(message="Payroll created successfully!"), 201

@api.route("/employee/payroll", methods=["GET"])
@jwt_required()
def get_payroll():
    employee_id = get_jwt_identity()
    
    payrolls = Payroll.query.filter_by(employee_id=employee_id).all()
    
    return jsonify([payroll.serialize() for payroll in payrolls])

@api.route("/employee/payroll/<int:payroll_id>", methods=["GET"])
@jwt_required()
def get_payroll_by_id(payroll_id):
    employee_id = get_jwt_identity()
    
    payroll = Payroll.query.get(payroll_id)
    
    if payroll is None or payroll.employee_id != employee_id:
        return jsonify(message="Payroll not found"), 404
        
    return jsonify(payroll.serialize())

@api.route("/employee/payroll/<int:payroll_id>", methods=["PUT"])
@jwt_required()
def update_payroll(payroll_id):
    admin_id = get_jwt_identity()
    
    user = User.query.get(admin_id)
    
    if user.role != "admin":
        return jsonify(message="You are not authorized to perform this action"), 403
    
    payroll = Payroll.query.get(payroll_id)
    
    if payroll is None:
        return jsonify(message="Payroll not found"), 404
    
    request_body = request.get_json()
    
    pay_date = request_body.get("pay_date")
    hours_worked = request_body.get("hours_worked")
    hourly_rate = request_body.get("hourly_rate")
    tax_deduction = request_body.get("tax_deduction")
    gross_salary = hours_worked * hourly_rate
    net_salary = gross_salary - tax_deduction
    
    if pay_date:
        payroll.pay_date = pay_date
        
    if hours_worked:
        payroll.hours_worked = hours_worked
        
    if hourly_rate:
        payroll.hourly_rate = hourly_rate
        
    if tax_deduction:
        payroll.tax_deduction = tax_deduction
    
    if hours_worked or hourly_rate or tax_deduction:
        payroll.gross_salary = gross_salary
        payroll.net_salary = net_salary
    
    db.session.commit()
    
    return jsonify(message="Payroll updated successfully!")

@api.route("/employee/payroll/<int:payroll_id>", methods=["DELETE"])
@jwt_required()
def delete_payroll(payroll_id):
    admin_id = get_jwt_identity()
    
    user = User.query.get(admin_id)
    
    if user.role != "admin":
        return jsonify(message="You are not authorized to perform this action"), 403
    
    payroll = Payroll.query.get(payroll_id)
    
    if payroll is None:
        return jsonify(message="Payroll not found"), 404
    
    db.session.delete(payroll)
    db.session.commit()
    
    return jsonify(message="Payroll deleted successfully!")

@api.route("/employee/dashboard", methods=["GET"])
@jwt_required()
def employee_dashboard():
    employee_id = get_jwt_identity()
    
    employee = Employee.query.get(employee_id)
    
    if employee is None:
        return jsonify(message="Employee not found"), 404
        
    return jsonify(employee.serialize())

@api.route("/employee/attendance", methods=["GET"])
@jwt_required()
def get_attendance():
    employee_id = get_jwt_identity()
    
    attendances = Attendance.query.filter_by(employee_id=employee_id).all()
    
    return jsonify([attendance.serialize() for attendance in attendances])

@api.route("/employee/attendance/<int:attendance_id>", methods=["GET"])
@jwt_required()
def get_attendance_by_id(attendance_id):
    employee_id = get_jwt_identity()
    
    attendance = Attendance.query.get(attendance_id)
    
    if attendance is None or attendance.employee_id != employee_id:
        return jsonify(message="Attendance not found"), 404
        
    return jsonify(attendance.serialize())

@api.route("/employee/attendance", methods=["POST"])
@jwt_required()
def create_attendance():
    employee_id = get_jwt_identity()
    
    request_body = request.get_json()
    
    date = request_body.get("date")
    status = request_body.get("status")
    
    if not date or not status:
        return jsonify(message="All fields are required"), 400
    
    if status not in ["present", "absent", "leave"]:
        return jsonify(message="Invalid status"), 400
    
    new_attendance = Attendance(employee_id=employee_id, date=date, status=status)
    
    db.session.add(new_attendance)
    db.session.commit()
    
    return jsonify(message="Attendance created successfully!"), 201

@api.route("/employee/attendance/<int:attendance_id>", methods=["PUT"])
@jwt_required()
def update_attendance(attendance_id):
    employee_id = get_jwt_identity()
    
    attendance = Attendance.query.get(attendance_id)
    
    if attendance is None or attendance.employee_id != employee_id:
        return jsonify(message="Attendance not found"), 404
    
    request_body = request.get_json()
    
    date = request_body.get("date")
    status = request_body.get("status")
    
    if date:
        attendance.date = date
        
    if status and status in ["present", "absent", "leave"]:
        attendance.status = status
    
    if status and status not in ["present", "absent", "leave"]:
        return jsonify(message="Invalid status"), 400
        
    db.session.commit()
    
    return jsonify(message="Attendance updated successfully!")