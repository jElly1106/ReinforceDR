from common.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import json
from datetime import datetime, timedelta

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    # 其他字段...
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self):
        # 生成JWT令牌
        identity = json.dumps({"id": self.id})
        return create_access_token(identity=identity)
        
    def to_dict(self):
        # 返回用户信息字典
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            # 其他需要返回的字段...
        }

class RetinalImage(db.Model):
    """眼底视网膜图像表"""
    __tablename__ = 'retinal_image'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)  # 存储图像的路径
    image_name = db.Column(db.String(100), nullable=False)  # 图像名称
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)  # 上传时间
    description = db.Column(db.Text, nullable=True)  # 图像描述或备注
    
    # 建立与用户的关系
    user = db.relationship('User', backref=db.backref('retinal_images', lazy=True))
    
    # 建立与分割结果的关系
    segmentation_results = db.relationship('SegmentationResult', backref='original_image', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_path': self.image_path,
            'image_name': self.image_name,
            'upload_time': self.upload_time.strftime('%Y-%m-%d %H:%M:%S'),
            'description': self.description
        }


class SegmentationResult(db.Model):
    """分割结果表"""
    __tablename__ = 'segmentation_result'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_id = db.Column(db.Integer, db.ForeignKey('retinal_image.id'), nullable=False)
    he_path = db.Column(db.String(255), nullable=True)  # 出血(HE)分割结果路径
    ex_path = db.Column(db.String(255), nullable=True)  # 硬性渗出(EX)分割结果路径
    ma_path = db.Column(db.String(255), nullable=True)  # 微血管瘤(MA)分割结果路径
    se_path = db.Column(db.String(255), nullable=True)  # 软性渗出(SE)分割结果路径
    combined_path = db.Column(db.String(255), nullable=True)  # 组合结果路径
    process_time = db.Column(db.DateTime, default=datetime.utcnow)  # 处理时间
    status = db.Column(db.String(20), default='completed')  # 处理状态：processing, completed, failed
    available_models = db.Column(db.String(255), default='') # 记录可用的模型类型

    def to_dict(self):
        return {
            'id': self.id,
            'image_id': self.image_id,
            'he_path': self.he_path,
            'ex_path': self.ex_path,
            'ma_path': self.ma_path,
            'se_path': self.se_path,
            'combined_path': self.combined_path,
            'process_time': self.process_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'available_models': self.available_models.split(',') if self.available_models else []
        }

