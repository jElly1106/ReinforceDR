from flask import Blueprint, request, jsonify, current_app,send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import json
import uuid
import threading  # 添加这一行导入threading模块

from datetime import datetime
from werkzeug.utils import secure_filename
from common.extensions import db
from database.models import User, RetinalImage, SegmentationResult
from core.segmentation_tasks import process_segmentation  # 确保也导入了这个函数

# 创建蓝图
retinal_bp = Blueprint('retinal', __name__)

# 允许的图像文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#图片访问API
@retinal_bp.route('/image/<path:image_path>', methods=['GET'])
def get_image(image_path):
    """获取图片文件的API"""
    try:
        # 构建完整的文件路径
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_path)
        
        # 检查文件是否存在
        if not os.path.exists(full_path):
            return jsonify({'code': 404, 'message': '图片不存在'}), 404
            
        # 返回图片文件
        return send_file(full_path)
        
    except Exception as e:
        current_app.logger.error(f"获取图片失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500

@retinal_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_image():
    """上传眼底图像API"""
    try:
        # 获取当前用户ID
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'code': 400, 'message': '没有上传文件'}), 400
            
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({'code': 400, 'message': '未选择文件'}), 400
            
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({'code': 400, 'message': '不支持的文件类型'}), 400
            
        # 生成安全的文件名
        original_filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4().hex}_{original_filename}"
        
        # 确保上传目录存在
        relative_path = os.path.join('retinal_images', str(user_id))
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
            user_id=user_id,
            image_url=image_url,  # 存储URL
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
        # 在生产环境中，应该使用Celery等任务队列
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
                'segmentation_id': segmentation.id
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
        # 获取当前用户ID
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        
        # 查询分割结果
        segmentation = SegmentationResult.query.get(segmentation_id)
        
        if not segmentation:
            return jsonify({'code': 404, 'message': '分割结果不存在'}), 404
            
        # 检查权限（确保用户只能查看自己的图像分割结果）
        retinal_image = RetinalImage.query.get(segmentation.image_id)
        if not retinal_image or retinal_image.user_id != user_id:
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
    """获取用户历史分割记录的API"""
    try:
        # 获取当前用户ID
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        
        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 查询用户的所有眼底图像，按上传时间倒序排列
        query = RetinalImage.query.filter_by(user_id=user_id).order_by(RetinalImage.upload_time.desc())
        
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
                'current_page': page
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
        # 获取当前用户ID
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        
        # 查询分割结果
        segmentation = SegmentationResult.query.get(segmentation_id)
        
        if not segmentation:
            return jsonify({'code': 404, 'message': '分割结果不存在'}), 404
            
        # 检查权限
        retinal_image = RetinalImage.query.get(segmentation.image_id)
        if not retinal_image or retinal_image.user_id != user_id:
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
        # 获取当前用户ID
        identity = json.loads(get_jwt_identity())
        user_id = identity.get('id')
        
        # 查询分割结果
        segmentation = SegmentationResult.query.get(segmentation_id)
        
        if not segmentation:
            return jsonify({'code': 404, 'message': '分割结果不存在'}), 404
            
        # 检查权限
        retinal_image = RetinalImage.query.get(segmentation.image_id)
        if not retinal_image or retinal_image.user_id != user_id:
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