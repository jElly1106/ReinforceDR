from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message
from database.models import User, Patient, DoctorPatientRelation, ROLE_PATIENT, ROLE_DOCTOR, ROLE_ADMIN
from werkzeug.security import check_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from common.utils import upload_images
import os
from datetime import datetime, timedelta
import uuid
import random
import string
import json

user_bp = Blueprint('user', __name__)

@user_bp.route('/send-captcha', methods=['POST'])
def send_captcha():
    """发送邮箱验证码"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    # 生成6位数字验证码
    captcha_code = ''.join(random.choices(string.digits, k=6))
    captcha_id = str(uuid.uuid4())
    
    # 将验证码存储到Redis，设置5分钟过期
    redis_client = current_app.config['redis_client']
    redis_client.setex(f'captcha:{captcha_id}', 300, captcha_code)  # 300秒 = 5分钟
    
    # 发送邮件
    try:
        mail = current_app.config['mail']
        msg = Message(
            subject='ReinforceDR 注册验证码',
            recipients=[email],
            body=f'您的验证码是：{captcha_code}，有效期5分钟。'
        )
        mail.send(msg)
        
        return jsonify({
            'message': 'Captcha sent successfully',
            'captcha_id': captcha_id
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'发送邮件失败: {str(e)}')
        return jsonify({'error': 'Failed to send email'}), 500

@user_bp.route('/register', methods=['POST'])
def register():
    """注册用户并验证邮箱验证码"""
    data = request.get_json()
    email = data['email']
    input_captcha = data['captcha']
    captcha_id = data['captcha_id']
    role = data.get('role', ROLE_PATIENT)  # 默认为患者角色

    if not email or not input_captcha or not captcha_id:
        return jsonify({'error': 'email, captcha, and captcha_id are required'}), 400

    # 验证角色是否有效
    if role not in [ROLE_PATIENT, ROLE_DOCTOR, ROLE_ADMIN]:
        return jsonify({'error': 'Invalid role'}), 400

    # 验证验证码
    redis_client = current_app.config['redis_client']
    stored_captcha = redis_client.get(f'captcha:{captcha_id}')
    
    if not stored_captcha:
        return jsonify({'error': 'Captcha expired or invalid'}), 400
    
    if stored_captcha.decode('utf-8') != input_captcha:
        return jsonify({'error': 'Invalid captcha'}), 400
    
    # 验证码正确，删除Redis中的验证码
    redis_client.delete(f'captcha:{captcha_id}')
    
    # 检查邮箱是否已注册
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    # 创建新用户
    new_user = User(
        username=data.get('username', '暂无'),
        email=email,
        password=data['password'],
        role=role
    )
    # 单独设置avatar字段
    new_user.avatar = data.get('avatar', '')
    
    db = current_app.config['db']
    db.session.add(new_user)
    db.session.commit()

    # 如果是患者角色，创建患者信息记录
    if role == ROLE_PATIENT:
        patient_info = Patient(
            user_id=new_user.id,
            name=data.get('name', data.get('nickname', '暂无')),  # 使用name字段，如果没有则用nickname
            gender=data.get('gender'),
            age=data.get('age'),
            phone=data.get('phone')  # 使用phone替代contact_number
        )
        db.session.add(patient_info)
        db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    """Log in the user.

    Returns:
        A json object consists of message.
    """
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        token = user.generate_token()
        return jsonify({
            'token': token, 
            'user_id': user.id,
            'role': user.role,  # 返回用户角色
            'is_admin': user.is_admin(),
            'is_doctor': user.is_doctor(),
            'is_patient': user.is_patient(),
            "message": "Login successful",
        }), 200
    return jsonify({'error': 'Invalid email or password'}), 400

@user_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """获取用户列表（仅管理员可访问）"""
    user_data = get_jwt_identity()
    user_data = json.loads(user_data)
    current_user = User.query.get(user_data['id'])
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    role_filter = request.args.get('role')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = User.query
    if role_filter and role_filter in [ROLE_PATIENT, ROLE_DOCTOR, ROLE_ADMIN]:
        query = query.filter_by(role=role_filter)
    
    users = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    }), 200

@user_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
def update_user_role(user_id):
    """更新用户角色（仅管理员可操作）"""
    user_data = get_jwt_identity()
    user_data = json.loads(user_data)
    current_user = User.query.get(user_data['id'])
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    target_user = User.query.get_or_404(user_id)
    data = request.get_json()
    new_role = data.get('role')
    
    if new_role not in [ROLE_PATIENT, ROLE_DOCTOR, ROLE_ADMIN]:
        return jsonify({'error': 'Invalid role'}), 400
    
    # 如果从患者角色改为其他角色，需要处理患者信息
    if target_user.role == ROLE_PATIENT and new_role != ROLE_PATIENT:
        # 可以选择删除患者信息或保留
        pass
    
    # 如果改为患者角色但没有患者信息，创建患者信息
    if new_role == ROLE_PATIENT and not target_user.patient_info:
        patient_info = Patient(user_id=target_user.id)
        db = current_app.config['db']
        db.session.add(patient_info)
    
    target_user.role = new_role
    db = current_app.config['db']
    db.session.commit()
    
    return jsonify({'message': 'User role updated successfully'}), 200

@user_bp.route('/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    """获取医生列表"""
    user_data = get_jwt_identity()
    user_data = json.loads(user_data)
    current_user = User.query.get(user_data['id'])
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # 只有管理员和医生可以查看医生列表
    if not (current_user.is_admin() or current_user.is_doctor()):
        return jsonify({'error': 'Access denied'}), 403
    
    doctors = User.query.filter_by(role=ROLE_DOCTOR).all()
    return jsonify({
        'doctors': [doctor.to_dict() for doctor in doctors]
    }), 200

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户的个人资料，包括头像 URL"""
    user_data = get_jwt_identity()
    user_data = json.loads(user_data)
    user = User.query.get_or_404(user_data['id'])
    
    profile_data = user.to_dict()
    
    # 如果是患者，添加患者详细信息
    if user.is_patient() and user.patient_info:
        profile_data.update(user.patient_info.to_dict())
    
    return jsonify(profile_data), 200

@user_bp.route('/doctor-patient-relations', methods=['POST'])
@jwt_required()
def create_doctor_patient_relation():
    """创建医生-患者关系（仅管理员可操作）"""
    user_data = get_jwt_identity()
    user_data = json.loads(user_data)
    current_user = User.query.get(user_data['id'])
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    patient_id = data.get('patient_id')
    
    if not doctor_id or not patient_id:
        return jsonify({'error': 'doctor_id and patient_id are required'}), 400
    
    # 验证医生和患者存在且角色正确
    doctor = User.query.get(doctor_id)
    patient = User.query.get(patient_id)
    
    if not doctor or not doctor.is_doctor():
        return jsonify({'error': 'Invalid doctor'}), 400
    
    if not patient or not patient.is_patient():
        return jsonify({'error': 'Invalid patient'}), 400
    
    # 检查关系是否已存在
    existing_relation = DoctorPatientRelation.query.filter_by(
        doctor_id=doctor_id, patient_id=patient_id
    ).first()
    
    if existing_relation:
        return jsonify({'error': 'Relation already exists'}), 400
    
    # 创建关系
    relation = DoctorPatientRelation(
        doctor_id=doctor_id,
        patient_id=patient_id
    )
    
    db = current_app.config['db']
    db.session.add(relation)
    db.session.commit()
    
    return jsonify({'message': 'Doctor-patient relation created successfully'}), 201

@user_bp.route('/doctor-patient-relations/<int:relation_id>', methods=['DELETE'])
@jwt_required()
def delete_doctor_patient_relation(relation_id):
    """删除医生-患者关系（仅管理员可操作）"""
    user_data = get_jwt_identity()
    user_data = json.loads(user_data)
    current_user = User.query.get(user_data['id'])
    
    if not current_user or not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    relation = DoctorPatientRelation.query.get_or_404(relation_id)
    
    db = current_app.config['db']
    db.session.delete(relation)
    db.session.commit()
    
    return jsonify({'message': 'Doctor-patient relation deleted successfully'}), 200