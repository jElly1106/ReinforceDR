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