from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # ใช้ String(256) เพื่อรองรับ hashed password
    role = db.Column(db.String(20), default='user')
    
    def is_admin(self):
        return self.role == 'admin'

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    file = db.Column(db.String(200))
    contact = db.Column(db.String(100))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id', name='fk_report_status'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    status = db.relationship('Status', backref='status_reports')  # เปลี่ยนจาก 'reports' เป็น 'status_reports'

    def __repr__(self):
        return f'<Report {self.title} - {self.status.name}>'

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(200))

    def __repr__(self):
        return f'<Status {self.name}>'
