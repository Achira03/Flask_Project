from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from forms import LoginForm, ReportForm, RegisterForm  
from models import db, User, Report

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # ใช้ฟอร์ม LoginForm
    if form.validate_on_submit():  # ถ้าผู้ใช้กด Submit
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()  # ค้นหาผู้ใช้จากฐานข้อมูล
        
        if user and user.password == password:  # ตรวจสอบว่า username และ password ถูกต้อง
            login_user(user)
            return redirect(url_for('dashboard'))  # ถ้าล็อกอินสำเร็จไปหน้า dashboard
        else:
            flash('Username หรือ Password ไม่ถูกต้อง', 'danger')  # ถ้าไม่ถูกต้องแสดงข้อความ
            return redirect(url_for('login'))  # กลับไปหน้า login
    return render_template('login.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)