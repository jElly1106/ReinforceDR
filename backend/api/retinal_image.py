from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import json
import uuid
import threading

from datetime import datetime
from werkzeug.utils import secure_filename
from common.extensions import db
from database.models import User, RetinalImage, SegmentationResult, Patient, DoctorPatientRelation, ROLE_PATIENT, ROLE_DOCTOR, ROLE_ADMIN
from core.segmentation_tasks import process_segmentation

retinal_bp = Blueprint('retinal', __name__)

@retinal_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_image():
    """上传眼底图像API"""
    try:
        # 获取当前用户信息
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 获取患者ID（可选参数，用于医生为患者上传）
        patient_id = request.form.get('patient_id')
        
        # 如果指定了患者ID，检查权限
        if patient_id:
            patient_id = int(patient_id)
            if not current_user.can_upload_for_patient(patient_id):
                return jsonify({'code': 403, 'message': '没有权限为该患者上传图像'}), 403
        else:
            # 如果没有指定患者ID，默认为当前用户（仅限患者）
            if current_user.is_patient():
                patient_id = user_id
            else:
                return jsonify({'code': 400, 'message': '医生用户必须指定患者ID'}), 400
        
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'code': 400, 'message': '没有上传文件'}), 400
            
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({'code': 400, 'message': '未选择文件'}), 400
            
            
        # 生成安全的文件名
        original_filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4().hex}_{original_filename}"
        
        # 确保上传目录存在（按患者ID组织）
        relative_path = os.path.join('retinal_images', str(patient_id))
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], relative_path)
        os.makedirs(upload_folder, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # 构建图片URL
        image_url = f"/api/retinal/image/{relative_path}/{filename}"
        
        # 获取描述信息
        description = request.form.get('description', '')
        
        # 保存到数据库
        new_image = RetinalImage(
            patient_id=patient_id,  # 患者ID
            uploaded_by=user_id,    # 上传者ID
            image_url=image_url,
            image_name=original_filename,
            description=description
        )
        
        db.session.add(new_image)
        db.session.commit()
        
        # 创建分割结果记录
        segmentation = SegmentationResult(
            image_id=new_image.id,
            status='processing'
        )
        db.session.add(segmentation)
        db.session.commit()
        
        # 使用线程异步调用模型进行分割
        thread = threading.Thread(
            target=process_segmentation,
            args=(new_image.id, segmentation.id, current_app._get_current_object())
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'code': 200, 
            'message': '图像上传成功，正在处理',
            'data': {
                'image_id': new_image.id,
                'segmentation_id': segmentation.id,
                'patient_id': patient_id,
                'uploaded_by': user_id
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"上传图像失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@retinal_bp.route('/segmentation/<int:segmentation_id>', methods=['GET'])
@jwt_required()
def get_segmentation_result(segmentation_id):
    """获取特定分割结果的API"""
    try:
        # 获取当前用户信息
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 查询分割结果
        segmentation = SegmentationResult.query.get(segmentation_id)
        
        if not segmentation:
            return jsonify({'code': 404, 'message': '分割结果不存在'}), 404
            
        # 检查权限
        retinal_image = RetinalImage.query.get(segmentation.image_id)
        if not retinal_image or not current_user.can_view_image(retinal_image):
            return jsonify({'code': 403, 'message': '没有权限查看此分割结果'}), 403
            
        # 返回分割结果
        result = segmentation.to_dict()
        # 添加原始图像信息
        result['original_image'] = retinal_image.to_dict()
        
        return jsonify({
            'code': 200,
            'message': '获取分割结果成功',
            'data': result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取分割结果失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@retinal_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """获取历史分割记录的API"""
    try:
        # 获取当前用户信息
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 获取查询参数
        patient_id = request.args.get('patient_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 根据用户角色确定查询范围
        if current_user.is_patient():
            # 患者只能查看自己的记录
            query_patient_id = user_id
        elif current_user.is_doctor():
            # 医生可以查看指定患者的记录（如果有权限）
            if patient_id:
                if not current_user.can_view_image(type('obj', (object,), {'patient_id': patient_id})()):
                    return jsonify({'code': 403, 'message': '没有权限查看该患者的记录'}), 403
                query_patient_id = patient_id
            else:
                # 如果没有指定患者ID，返回错误
                return jsonify({'code': 400, 'message': '医生用户必须指定患者ID'}), 400
        elif current_user.is_admin():
            # 管理员可以查看任何患者的记录
            if patient_id:
                query_patient_id = patient_id
            else:
                return jsonify({'code': 400, 'message': '管理员用户必须指定患者ID'}), 400
        else:
            return jsonify({'code': 403, 'message': '无效的用户角色'}), 403
        
        # 查询指定患者的所有眼底图像，按上传时间倒序排列
        query = RetinalImage.query.filter_by(patient_id=query_patient_id).order_by(RetinalImage.upload_time.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page)
        
        # 构建响应数据
        items = []
        for image in pagination.items:
            image_data = image.to_dict()
            # 获取最新的分割结果
            latest_segmentation = SegmentationResult.query.filter_by(image_id=image.id).order_by(SegmentationResult.process_time.desc()).first()
            if latest_segmentation:
                image_data['segmentation'] = latest_segmentation.to_dict()
            items.append(image_data)
        
        return jsonify({
            'code': 200,
            'message': '获取历史记录成功',
            'data': {
                'items': items,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'patient_id': query_patient_id
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取历史记录失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@retinal_bp.route('/segmentation/status/<int:segmentation_id>', methods=['GET'])
@jwt_required()
def check_segmentation_status(segmentation_id):
    """检查分割状态的API"""
    try:
        # 获取当前用户信息
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 查询分割结果
        segmentation = SegmentationResult.query.get(segmentation_id)
        
        if not segmentation:
            return jsonify({'code': 404, 'message': '分割结果不存在'}), 404
            
        # 检查权限
        retinal_image = RetinalImage.query.get(segmentation.image_id)
        if not retinal_image or not current_user.can_view_image(retinal_image):
            return jsonify({'code': 403, 'message': '没有权限查看此分割结果'}), 403
            
        # 返回状态
        return jsonify({
            'code': 200,
            'message': '获取分割状态成功',
            'data': {
                'segmentation_id': segmentation.id,
                'status': segmentation.status,
                'process_time': segmentation.process_time.strftime('%Y-%m-%d %H:%M:%S') if segmentation.process_time else None
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取分割状态失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@retinal_bp.route('/segmentation/progress/<int:segmentation_id>', methods=['GET'])
@jwt_required()
def get_segmentation_progress(segmentation_id):
    """获取分割进度的API"""
    try:
        # 获取当前用户信息
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 查询分割结果
        segmentation = SegmentationResult.query.get(segmentation_id)
        
        if not segmentation:
            return jsonify({'code': 404, 'message': '分割结果不存在'}), 404
            
        # 检查权限
        retinal_image = RetinalImage.query.get(segmentation.image_id)
        if not retinal_image or not current_user.can_view_image(retinal_image):
            return jsonify({'code': 403, 'message': '没有权限查看此分割结果'}), 403
            
        # 返回进度信息
        return jsonify({
            'code': 200,
            'message': '获取分割进度成功',
            'data': {
                'segmentation_id': segmentation.id,
                'status': segmentation.status,
                'progress': segmentation.progress,
                'error_message': segmentation.error_message,
                'process_time': segmentation.process_time.strftime('%Y-%m-%d %H:%M:%S') if segmentation.process_time else None
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取分割进度失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@retinal_bp.route('/segmentation/<int:segmentation_id>', methods=['DELETE'])
@jwt_required()
def delete_segmentation(segmentation_id):
    """删除分割记录"""
    try:
        # 获取当前用户信息
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 查询分割结果
        segmentation = SegmentationResult.query.get(segmentation_id)
        
        if not segmentation:
            return jsonify({'code': 404, 'message': '分割结果不存在'}), 404
            
        # 检查权限 - 获取关联的图像
        retinal_image = RetinalImage.query.get(segmentation.image_id)
        if not retinal_image:
            return jsonify({'code': 404, 'message': '关联的图像不存在'}), 404
            
        # 权限检查：只有管理员、上传图像的医生或拥有该患者管理权限的医生可以删除
        can_delete = False
        
        if current_user.is_admin():
            can_delete = True
        elif current_user.is_doctor():
            # 检查是否是上传者或者有患者管理权限
            if (retinal_image.uploaded_by == user_id or 
                DoctorPatientRelation.query.filter_by(
                    doctor_id=user_id, 
                    patient_id=retinal_image.patient_id
                ).first()):
                can_delete = True
        
        if not can_delete:
            return jsonify({'code': 403, 'message': '没有权限删除此分割结果'}), 403
        
        # 删除相关的分割结果文件（如果存在）
        import os
        from flask import current_app
        
        file_urls = [
            segmentation.he_url,
            segmentation.ex_url, 
            segmentation.ma_url,
            segmentation.se_url,
            segmentation.combined_url
        ]
        
        # 删除物理文件
        for file_url in file_urls:
            if file_url:
                try:
                    # 从URL提取文件路径
                    if file_url.startswith('/api/retinal/image/'):
                        relative_path = file_url[len('/api/retinal/image/'):]
                        file_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), relative_path)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            current_app.logger.info(f"已删除分割结果文件: {file_path}")
                except Exception as file_error:
                    current_app.logger.warning(f"删除文件失败: {file_url}, 错误: {str(file_error)}")
        
        # 删除数据库记录
        db.session.delete(segmentation)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '分割记录删除成功',
            'data': {
                'deleted_segmentation_id': segmentation_id,
                'image_id': segmentation.image_id
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除分割记录失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500