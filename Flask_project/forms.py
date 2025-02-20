from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ReportForm(FlaskForm):
    title = StringField('หัวข้อปัญหา', validators=[DataRequired()])
    description = TextAreaField('รายละเอียด', validators=[DataRequired()])
    category = SelectField('หมวดหมู่', choices=[
            ('building', 'ปัญหาด้านอาคารสถานที่'),
            ('it', 'ปัญหาด้านระบบไอทีและอินเทอร์เน็ต'),
            ('admin', 'ปัญหาด้านเอกสารและงานธุรการ'),
            ('welfare', 'ปัญหาด้านกิจกรรมและสวัสดิการนักศึกษา'),
            ('safety', 'ปัญหาด้านความปลอดภัย'),
            ('other', 'ปัญหาทั่วไปอื่นๆ')
        ], validators=[DataRequired()])
    file = FileField('แนบไฟล์หรือรูปภาพ')
    contact = StringField('ข้อมูลติดต่อเพิ่มเติม')
    submit = SubmitField('ส่งเรื่อง')
        
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
