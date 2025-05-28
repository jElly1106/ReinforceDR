from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from datetime import datetime
from common.extensions import db
from database.models import User, Patient, DoctorPatientRelation, RetinalImage, ROLE_PATIENT, ROLE_DOCTOR, ROLE_ADMIN
from sqlalchemy import and_, or_

# 创建蓝图
patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/add-patient', methods=['POST'])
@jwt_required()
def add_patient():
    """医生添加新患者（不需要用户账号）"""
    try:
        # 获取当前用户信息
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 检查权限
        if not (current_user.is_doctor() or current_user.is_admin()):
            return jsonify({'code': 403, 'message': '权限不足，只有医生和管理员可以添加患者'}), 403
        
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({'code': 400, 'message': '患者姓名是必填字段'}), 400
        
        # 创建患者信息
        new_patient = Patient(
            name=data['name'],
            gender=data.get('gender'),
            age=data.get('age'),
            phone=data.get('phone')
        )
        
        db.session.add(new_patient)
        db.session.flush()  # 获取新患者的ID
        
        # 如果是医生添加患者，建立医生-患者关系
        if current_user.is_doctor():
            relation = DoctorPatientRelation(
                doctor_id=user_id,
                patient_id=new_patient.id
            )
            db.session.add(relation)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '患者添加成功',
            'data': {
                'patient_id': new_patient.id,
                'name': new_patient.name,
                'gender': new_patient.gender,
                'age': new_patient.age,
                'phone': new_patient.phone
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"添加患者失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@patient_bp.route('/my-patients', methods=['GET'])
@jwt_required()
def get_my_patients():
    """获取医生管理的所有患者信息"""
    try:
        # 获取当前用户信息
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 检查权限
        if not (current_user.is_doctor() or current_user.is_admin()):
            return jsonify({'code': 403, 'message': '权限不足，只有医生和管理员可以查看患者信息'}), 403
        
        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if current_user.is_admin():
            # 管理员可以查看所有患者
            query = Patient.query
        else:
            # 医生只能查看自己管理的患者
            relations = DoctorPatientRelation.query.filter_by(doctor_id=user_id).all()
            patient_ids = [r.patient_id for r in relations]
            if not patient_ids:
                return jsonify({
                    'code': 200,
                    'message': '获取患者列表成功',
                    'data': {
                        'items': [],
                        'total': 0,
                        'pages': 0,
                        'current_page': page
                    }
                }), 200
            query = Patient.query.filter(Patient.id.in_(patient_ids))
        
        # 分页查询
        pagination = query.paginate(page=page, per_page=per_page)
        
        # 构建响应数据
        items = []
        for patient in pagination.items:
            patient_data = patient.to_dict()
            
            # 获取患者的图像数量
            image_count = RetinalImage.query.filter_by(patient_id=patient.id).count()
            patient_data['image_count'] = image_count
            
            items.append(patient_data)
        
        return jsonify({
            'code': 200,
            'message': '获取患者列表成功',
            'data': {
                'items': items,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取患者列表失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@patient_bp.route('/update-patient/<int:patient_id>', methods=['PUT'])
@jwt_required()
def update_patient(patient_id):
    """修改患者信息"""
    try:
        # 获取当前用户信息
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 检查权限
        if not (current_user.is_doctor() or current_user.is_admin()):
            return jsonify({'code': 403, 'message': '权限不足'}), 403
        
        # 查找患者
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'code': 404, 'message': '患者不存在'}), 404
        
        # 医生只能修改自己管理的患者
        if current_user.is_doctor():
            relation = DoctorPatientRelation.query.filter_by(
                doctor_id=user_id, 
                patient_id=patient_id
            ).first()
            if not relation:
                return jsonify({'code': 403, 'message': '您没有权限修改此患者信息'}), 403
        
        data = request.get_json()
        
        # 更新患者信息
        if 'name' in data:
            patient.name = data['name']
        if 'gender' in data:
            patient.gender = data['gender']
        if 'age' in data:
            patient.age = data['age']
        if 'phone' in data:
            patient.phone = data['phone']
        
        patient.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '患者信息更新成功',
            'data': patient.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新患者信息失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@patient_bp.route('/search-patients', methods=['GET'])
@jwt_required()
def search_patients():
    """根据条件筛选患者"""
    try:
        # 获取当前用户信息
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 检查权限
        if not (current_user.is_doctor() or current_user.is_admin()):
            return jsonify({'code': 403, 'message': '权限不足'}), 403
        
        # 获取搜索参数
        keyword = request.args.get('keyword', '').strip()
        gender = request.args.get('gender', '').strip()
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 构建基础查询
        if current_user.is_admin():
            # 管理员可以搜索所有患者
            base_query = User.query.filter_by(role=ROLE_PATIENT)
        else:
            # 医生只能搜索自己管理的患者
            relations = DoctorPatientRelation.query.filter_by(doctor_id=user_id).all()
            patient_ids = [r.patient_id for r in relations]
            if not patient_ids:
                return jsonify({
                    'code': 200,
                    'message': '搜索完成',
                    'data': {
                        'items': [],
                        'total': 0,
                        'pages': 0,
                        'current_page': page
                    }
                }), 200
            base_query = User.query.filter(User.id.in_(patient_ids))
        
        # 添加搜索条件
        if keyword:
            base_query = base_query.filter(
                or_(
                    User.username.contains(keyword),
                    User.email.contains(keyword)
                )
            )
        
        # 如果有年龄或性别筛选，需要联接Patient表
        if gender or min_age is not None or max_age is not None:
            base_query = base_query.join(Patient, User.id == Patient.user_id)
            
            if gender:
                base_query = base_query.filter(Patient.gender == gender)
            
            if min_age is not None:
                base_query = base_query.filter(Patient.age >= min_age)
            
            if max_age is not None:
                base_query = base_query.filter(Patient.age <= max_age)
        
        # 分页查询
        pagination = base_query.paginate(page=page, per_page=per_page)
        
        # 构建响应数据
        items = []
        for patient_user in pagination.items:
            patient_data = patient_user.to_dict()
            # 获取患者详细信息
            patient_info = Patient.query.filter_by(user_id=patient_user.id).first()
            if patient_info:
                patient_data.update(patient_info.to_dict())
            
            # 获取患者的图像数量
            image_count = RetinalImage.query.filter_by(patient_id=patient_user.id).count()
            patient_data['image_count'] = image_count
            
            items.append(patient_data)
        
        return jsonify({
            'code': 200,
            'message': '搜索完成',
            'data': {
                'items': items,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'search_params': {
                    'keyword': keyword,
                    'gender': gender,
                    'min_age': min_age,
                    'max_age': max_age
                }
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"搜索患者失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@patient_bp.route('/delete-patient/<int:patient_id>', methods=['DELETE'])
@jwt_required()
def delete_patient(patient_id):
    """删除患者"""
    try:
        # 获取当前用户信息
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 检查权限
        if not (current_user.is_doctor() or current_user.is_admin()):
            return jsonify({'code': 403, 'message': '权限不足'}), 403
        
        # 查找患者
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'code': 404, 'message': '患者不存在'}), 404
        
        # 医生只能删除自己管理的患者
        if current_user.is_doctor():
            relation = DoctorPatientRelation.query.filter_by(
                doctor_id=user_id, 
                patient_id=patient_id
            ).first()
            if not relation:
                return jsonify({'code': 403, 'message': '您没有权限删除此患者'}), 403
        
        # 检查患者是否有眼底图像数据
        image_count = RetinalImage.query.filter_by(patient_id=patient_id).count()
        if image_count > 0:
            return jsonify({
                'code': 400, 
                'message': f'无法删除患者，该患者还有 {image_count} 张眼底图像记录，请先删除相关图像数据'
            }), 400
        
        # 删除医生-患者关系
        DoctorPatientRelation.query.filter_by(patient_id=patient_id).delete()
        
        # 删除患者记录
        db.session.delete(patient)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '患者删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除患者失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@patient_bp.route('/patient-detail/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_detail(patient_id):
    """获取患者详细信息"""
    try:
        # 获取当前用户信息
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 检查权限
        if not (current_user.is_doctor() or current_user.is_admin()):
            return jsonify({'code': 403, 'message': '权限不足'}), 403
        
        # 直接查找患者（使用Patient表的ID）
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'code': 404, 'message': '患者不存在'}), 404
        
        # 医生只能查看自己管理的患者
        if current_user.is_doctor():
            relation = DoctorPatientRelation.query.filter_by(
                doctor_id=user_id, 
                patient_id=patient_id  # 现在使用Patient表的ID
            ).first()
            if not relation:
                return jsonify({'code': 403, 'message': '您没有权限查看此患者信息'}), 403
        
        # 获取患者基本信息
        patient_data = patient.to_dict()
        
        # 如果患者关联了用户账号，添加用户信息
        if patient.user_id and patient.user:
            user_info = patient.user.to_dict()
            patient_data['username'] = user_info.get('username')
            patient_data['email'] = user_info.get('email')
            patient_data['avatar'] = user_info.get('avatar')
        
        # 获取患者的眼底图像列表
        images = RetinalImage.query.filter_by(patient_id=patient_id).order_by(
            RetinalImage.upload_time.desc()
        ).all()
        
        patient_data['images'] = [img.to_dict() for img in images]
        patient_data['image_count'] = len(images)
        
        return jsonify({
            'code': 200,
            'message': '获取患者详细信息成功',
            'data': patient_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取患者详细信息失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500