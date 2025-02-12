from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    security_question_1 = db.Column(db.String(255))
    security_answer_1 = db.Column(db.String(255))
    role = db.Column(db.String(50), nullable=False)  # 'admin' or 'employee'
    created_at = db.Column(db.DateTime, default=datetime.now(tz=timezone.utc))

    def serialize(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }


class Employee(db.Model):
    __tablename__ = 'employees'
    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.user_id', ondelete='CASCADE'), unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    personal_email = db.Column(db.String(255), unique=True, nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    payrolls = db.relationship('Payroll', backref='employee', lazy=True)

    def serialize(self):
        return {
            'employee_id': self.employee_id,
            'user_id': self.user_id,
            'personal_email': self.personal_email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'address': self.address,
            'phone': self.phone,
            'position': self.position,
            'department': self.department,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'payrolls': [payroll.serialize() for payroll in self.payrolls]
        }


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    token_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id', ondelete='CASCADE'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

    def serialize(self):
        return {
            'token_id': self.token_id,
            'user_id': self.user_id,
            'token': self.token,
            'expires_at': self.expires_at.isoformat(),
            'used': self.used
        }


class Attendance(db.Model):
    __tablename__ = 'attendance'
    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey(
        'employees.employee_id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    # e.g., 'present', 'absent', 'leave'
    status = db.Column(db.String(50), nullable=False)

    def serialize(self):
        return {
            'attendance_id': self.attendance_id,
            'employee_id': self.employee_id,
            'date': self.date.isoformat(),
            'status': self.status
        }


class Deduction(db.Model):
    __tablename__ = 'deductions'
    deduction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey(
        'employees.employee_id', ondelete='CASCADE'), nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), default=0.0)
    insurance_premium = db.Column(db.Numeric(10, 2), default= 0.0)
    other_deductions = db.Column(db.Numeric(10, 2), default= 0.0)

    def serialize(self):
        return {
            'deduction_id': self.deduction_id,
            'employee_id': self.employee_id,
            'tax_rate': float(self.tax_rate),
            'insurance_premium': float(self.insurance_premium),
            'other_deductions': float(self.other_deductions)
        }


class Payroll(db.Model):
    __tablename__ = 'payroll'
    payroll_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey(
        'employees.employee_id', ondelete='CASCADE'), nullable=False)
    pay_date = db.Column(db.Date, nullable=False)
    hours_worked = db.Column(db.Numeric(5, 2), nullable=False)
    hourly_rate = db.Column(db.Numeric(10, 2), nullable=False)
    gross_salary = db.Column(db.Numeric(10, 2), nullable=False)
    net_salary = db.Column(db.Numeric(10, 2), nullable=False)
    tax_deduction = db.Column(db.Numeric(10, 2), nullable=False)

    def serialize(self):
        return {
            'payroll_id': self.payroll_id,
            'employee_id': self.employee_id,
            'pay_date': self.pay_date.isoformat(),
            'gross_salary': float(self.gross_salary),
            'net_salary': float(self.net_salary),
            'tax_deduction': float(self.tax_deduction),
            'hours_worked': float(self.hours_worked),
            'hourly_rate': float(self.hourly_rate)
        }