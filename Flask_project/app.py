import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy, pagination
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from forms import LoginForm, ReportForm, RegisterForm  
from models import db, User, Report, Status
from werkzeug.security import check_password_hash, generate_password_hash
from utils import admin_required, moderator_required
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.config.from_object('config.Config')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/Aj.bot/Flask_project/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'


db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # ใช้ db.session.get() แทน query.get()

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
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))  # ถ้าล็อกอินสำเร็จไปหน้า dashboard
        else:
            flash('Username หรือ Password ไม่ถูกต้อง', 'danger')  # ถ้าไม่ถูกต้องแสดงข้อความ
            return redirect(url_for('login'))  # กลับไปหน้า login
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # ดึงข้อมูลจากฟอร์ม
        username = form.username.data
        password = form.password.data

        # ตรวจสอบว่ามีชื่อผู้ใช้นี้ในระบบหรือยัง
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('ชื่อผู้ใช้นี้ถูกใช้แล้ว กรุณาเลือกชื่อใหม่', 'danger')
            return redirect(url_for('signup'))

        # สร้างผู้ใช้ใหม่
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password,)  
        db.session.add(new_user)
        db.session.commit()

        flash('สมัครสมาชิกสำเร็จ! กรุณาล็อกอิน', 'success')
        return redirect(url_for('login'))  

    return render_template('signup.html', form=form)  # หรือใช้ signup.html ได้

@app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    form = ReportForm()
    if form.validate_on_submit():
        file_path = None
        if form.file.data:
            filename = secure_filename(form.file.data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.file.data.save(file_path)

        new_report = Report(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            file=file_path,
            contact=form.contact.data,
            user_id=current_user.id
        )
        db.session.add(new_report)
        db.session.commit()
        flash('ส่งเรื่องเรียบร้อยแล้ว!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('report.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':  # ถ้าเป็นแอดมินให้เห็นทุกปัญหา
        reports = Report.query.options(joinedload(Report.status)).all()  # ใช้ joinedload เพื่อโหลด status
    else:
        reports = Report.query.filter_by(user_id=current_user.id).options(joinedload(Report.status)).all()  # ใช้ joinedload เพื่อโหลด status

    # ดึงปัญหาที่แจ้งล่าสุด (เรียงตามวันที่)
    recent_reports = Report.query.filter_by(user_id=current_user.id).options(joinedload(Report.status)) \
                                .order_by(Report.created_at.desc()).limit(5).all()  # ใช้ joinedload เพื่อโหลด status

    # นับจำนวนรายงานต่างๆ
    total_reports = len(reports)
    in_progress_reports = len([r for r in reports if r.status.name == 'กำลังดำเนินการ'])
    completed_reports = len([r for r in reports if r.status.name == 'เสร็จสิ้น'])

    return render_template('dashboard.html', 
                           reports=reports, 
                           recent_reports=recent_reports,
                           total_reports=total_reports, 
                           in_progress_reports=in_progress_reports,
                           completed_reports=completed_reports)

@app.route('/issues')
def issues():
    # รับค่าจาก query string 'status', 'category', และ 'page'
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    page = request.args.get('page', 1, type=int)  # กำหนดค่าเริ่มต้นเป็น 1 ถ้าไม่มีการระบุหน้า

    # ค้นหาสถานะที่ตรงกับค่าที่รับมา
    if status_filter:
        status = Status.query.filter_by(name=status_filter).first()
        if status:
            reports = Report.query.filter_by(status=status).paginate(page=page, per_page=10)
        else:
            reports = Report.query.paginate(page=page, per_page=10)
    else:
        reports = Report.query.paginate(page=page, per_page=10)

    # ถ้ามีการกรองหมวดหมู่
    if category_filter:
        reports = reports.filter_by(category=category_filter).paginate(page=page, per_page=10)

    return render_template('issues.html', reports=reports)

@app.route('/issues/status/<status>')
def issues_by_status(status):
    reports = Report.query.filter(Report.status == status).all()
    return render_template('issues.html', reports=reports, status=status)

@app.route('/issues/in-progress')
@login_required
def issues_in_progress():
    reports = Report.query.filter_by(status="กำลังดำเนินการ").all()
    return render_template('in_progress.html', reports=reports)

@app.route('/issues/completed')
@login_required
def issues_completed():
    reports = Report.query.filter_by(status="เสร็จสิ้น").all()
    return render_template('completed.html', reports=reports)


@app.route('/admin', methods=['GET', 'POST'])
@login_required  # ต้องล็อกอินก่อนเข้า
@admin_required  # ต้องเป็นแอดมินเท่านั้น
def admin_dashboard():
    users = User.query.all()  # ดึงรายชื่อผู้ใช้ทั้งหมด
    category_filter = request.args.get('category')  # ดึงหมวดหมู่ที่เลือกจาก URL

    # ดึงรายงานจากฐานข้อมูลตามหมวดหมู่ที่กรอง
    if category_filter:
        reports = Report.query.filter_by(category=category_filter).all()
    else:
        reports = Report.query.all()  # ดึงปัญหาทั้งหมดหากไม่มีการกรอง

    return render_template('admin.html', users=users, reports=reports)

@app.route('/admin/change_role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def change_role(user_id):
    user = User.query.get(user_id)
    if user:
        new_role = request.form.get('role')  # รับ role ใหม่จากฟอร์ม
        user.role = new_role
        db.session.commit()
        flash(f'เปลี่ยน Role ของ {user.username} เป็น {new_role} สำเร็จ!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f'ลบผู้ใช้ {user.username} สำเร็จ!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/update_report_status/<int:report_id>', methods=['POST'])
@login_required
@admin_required  # หรือแอดมินเท่านั้นที่สามารถอัปเดตสถานะได้
def update_report_status(report_id):
    report = Report.query.get_or_404(report_id)  # ค้นหารายงานจาก ID
    new_status = request.form.get('status')  # รับค่าสถานะใหม่จากฟอร์ม

    # ค้นหา status_id ที่ตรงกับชื่อ new_status
    status_obj = Status.query.filter_by(name=new_status).first()

    if status_obj:
        report.status_id = status_obj.id  # ✅ อัปเดต status_id ไม่ใช่ report.status
        db.session.commit()  # บันทึกการเปลี่ยนแปลง
        flash(f'สถานะของปัญหาหมายเลข {report.id} ถูกอัปเดตเป็น {new_status} แล้ว!', 'success')
    else:
        flash('ไม่พบสถานะที่เลือก กรุณาลองใหม่!', 'danger')

    return redirect(url_for('admin_dashboard'))  # กลับไปที่หน้าแอดมิน

@app.route('/admin_dashboard_1', methods=['GET'])
def admin_dashboard_1():
    category_filter = request.args.get('category')
    if category_filter:
        reports = Report.query.filter_by(category=category_filter).all()
    else:
        reports = Report.query.all()

    users = User.query.all()  # ดึงข้อมูลผู้ใช้ทั้งหมด

    return render_template('admin.html', reports=reports, users=users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)