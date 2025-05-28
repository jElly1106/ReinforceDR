from common.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import json
from datetime import datetime, timedelta

# 定义用户角色常量
ROLE_PATIENT = 'patient'
ROLE_DOCTOR = 'doctor'
ROLE_ADMIN = 'admin'

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_PATIENT)  # 用户角色
    avatar = db.Column(db.String(255), nullable=True)  # 头像路径
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, username, email, password, role=ROLE_PATIENT):
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self):
        """生成JWT令牌"""
        return create_access_token(identity=json.dumps({'id': self.id, 'role': self.role}))
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'avatar': self.avatar,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def is_admin(self):
        """检查是否为管理员"""
        return self.role == ROLE_ADMIN
    
    def is_doctor(self):
        """检查是否为医生"""
        return self.role == ROLE_DOCTOR
    
    def is_patient(self):
        """检查是否为患者"""
        return self.role == ROLE_PATIENT
    
    def can_view_image(self, image):
        """检查是否可以查看指定图像"""
        if self.is_admin():
            return True  # 管理员可以查看所有图像
        elif self.is_doctor():
            # 医生只能查看自己管理的患者的图像
            return DoctorPatientRelation.query.filter_by(
                doctor_id=self.id, 
                patient_id=image.patient_id
            ).first() is not None
        elif self.is_patient():
            # 患者只能查看自己的图像（通过user_id关联）
            patient = Patient.query.filter_by(user_id=self.id).first()
            return patient and image.patient_id == patient.id
        return False
    
    def can_upload_for_patient(self, patient_id):
        """检查是否可以为指定患者上传图像"""
        if self.is_admin():
            return True  # 管理员可以为任何患者上传
        elif self.is_doctor():
            # 医生只能为自己管理的患者上传
            return DoctorPatientRelation.query.filter_by(
                doctor_id=self.id, 
                patient_id=patient_id
            ).first() is not None
        elif self.is_patient():
            # 患者只能为自己上传
            patient = Patient.query.filter_by(user_id=self.id).first()
            return patient and patient_id == patient.id
        return False
    
    def get_accessible_patients(self):
        """获取可访问的患者列表"""
        if self.is_admin():
            # 管理员可以访问所有患者
            return Patient.query.all()
        elif self.is_doctor():
            # 医生只能访问自己管理的患者
            relations = DoctorPatientRelation.query.filter_by(doctor_id=self.id).all()
            patient_ids = [r.patient_id for r in relations]
            return Patient.query.filter(Patient.id.in_(patient_ids)).all()
        elif self.is_patient():
            # 患者只能访问自己
            patient = Patient.query.filter_by(user_id=self.id).first()
            return [patient] if patient else []
        return []

class Patient(db.Model):
    """患者信息表"""
    __tablename__ = 'patient'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 可空
    # 患者基本信息字段
    name = db.Column(db.String(80), nullable=False)  # 患者姓名
    gender = db.Column(db.String(10), nullable=True)  # 性别
    age = db.Column(db.Integer, nullable=True)  # 年龄
    phone = db.Column(db.String(20), nullable=True)  # 电话号码
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 与用户的关系（可选）
    user = db.relationship('User', backref=db.backref('patient_info', uselist=False, cascade="all, delete-orphan"), foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'phone': self.phone,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            # 如果有关联用户账号，返回用户信息
            'username': self.user.username if self.user else None,
            'email': self.user.email if self.user else None,
            'has_account': self.user_id is not None
        }
        
class DoctorPatientRelation(db.Model):
    """医生-患者关系表"""
    __tablename__ = 'doctor_patient_relation'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)  # 直接关联Patient表
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 关联时间
    
    # 与用户的关系
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref=db.backref('doctor_relations', lazy=True))
    patient = db.relationship('Patient', foreign_keys=[patient_id], backref=db.backref('doctor_relations', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'patient_id': self.patient_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class RetinalImage(db.Model):
    """眼底视网膜图像表"""
    __tablename__ = 'retinal_image'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)  # 直接关联Patient表
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 上传者ID（医生或管理员）
    image_url = db.Column(db.String(255), nullable=False)  # 存储图像的URL
    image_name = db.Column(db.String(100), nullable=False)  # 图像名称
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)  # 上传时间
    description = db.Column(db.Text, nullable=True)  # 图像描述或备注
    
    # 建立与患者的关系
    patient = db.relationship('Patient', backref=db.backref('images', lazy=True))
    # 建立与上传者的关系
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref=db.backref('uploaded_images', lazy=True))
    
    # 建立与分割结果的关系
    segmentation_results = db.relationship('SegmentationResult', backref='original_image', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'uploaded_by': self.uploaded_by,
            'image_url': self.image_url,
            'image_name': self.image_name,
            'upload_time': self.upload_time.strftime('%Y-%m-%d %H:%M:%S'),
            'description': self.description,
            'patient_name': self.patient.name if self.patient else None,
            'uploader_name': self.uploader.username if self.uploader else None
        }


class SegmentationResult(db.Model):
    """分割结果表"""
    __tablename__ = 'segmentation_result'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_id = db.Column(db.Integer, db.ForeignKey('retinal_image.id'), nullable=False)
    he_url = db.Column(db.String(255), nullable=True)  # 出血(HE)分割结果URL
    ex_url = db.Column(db.String(255), nullable=True)  # 硬性渗出(EX)分割结果URL
    ma_url = db.Column(db.String(255), nullable=True)  # 微血管瘤(MA)分割结果URL
    se_url = db.Column(db.String(255), nullable=True)  # 软性渗出(SE)分割结果URL
    combined_url = db.Column(db.String(255), nullable=True)  # 组合结果URL
    process_time = db.Column(db.DateTime, default=datetime.utcnow)  # 处理时间
    status = db.Column(db.String(20), default='completed')  # 处理状态：processing, completed, failed
    available_models = db.Column(db.String(255), default='') # 记录可用的模型类型
    progress = db.Column(db.Float, default=0.0)  # 分割进度，0-100的浮点数
    error_message = db.Column(db.Text, nullable=True) # 错误信息

    def to_dict(self):
        return {
            'id': self.id,
            'image_id': self.image_id,
            'he_url': self.he_url,
            'ex_url': self.ex_url,
            'ma_url': self.ma_url,
            'se_url': self.se_url,
            'combined_url': self.combined_url,
            'process_time': self.process_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'available_models': self.available_models.split(',') if self.available_models else [],
            'progress': self.progress,
            'error_message': self.error_message
        }