from functools import wraps
from flask import abort
from flask_login import current_user

# ตรวจสอบสิทธิ์ผู้ใช้ (เฉพาะ Admin เท่านั้น)
from functools import wraps
from flask import redirect, url_for, flash

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('คุณต้องเป็นแอดมินเพื่อเข้าถึงหน้านี้', 'danger')
            return redirect(url_for('index'))  # กลับไปหน้าแรก
        return f(*args, **kwargs)
    return decorated_function

# ตรวจสอบสิทธิ์ผู้ใช้ (เฉพาะ Admin และ Moderator)
def moderator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_admin() or current_user.is_moderator()):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
