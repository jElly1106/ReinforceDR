import os
from datetime import datetime
from common.extensions import db
from database.models import RetinalImage, SegmentationResult
from core.segmentation_model import RetinalSegmentationModel
from flask import current_app
import torch
from PIL import Image
import numpy as np

def process_segmentation(image_id, segmentation_id, app=None):
    """
    处理眼底图像分割的任务
    
    Args:
        image_id: 图像ID
        segmentation_id: 分割结果ID
        app: Flask应用实例
    """

    # 导入 current_app 并获取应用实例
    if app:
        ctx = app.app_context()
        ctx.push()
    else:
        ctx = None

    try:
        image = RetinalImage.query.get(image_id)
        segmentation = SegmentationResult.query.get(segmentation_id)
        
        if not image or not segmentation:
            print(f"找不到图像或分割记录: image_id={image_id}, segmentation_id={segmentation_id}")
            return
        
        # 更新状态为处理中
        segmentation.status = 'processing'
        segmentation.progress = 0.0
        db.session.commit()
    
        # 获取图像URL并转换为本地路径
        image_url = image.image_url
        user_id = image.user_id
                
        # 从URL中提取相对路径部分
        if image_url.startswith('/api/retinal/image/'):
            relative_path = image_url[len('/api/retinal/image/'):]
            # 确保使用正确的路径分隔符
            relative_path = relative_path.replace('/', os.path.sep)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], relative_path)
        else:
            # 如果URL不是以预期格式开头，尝试直接构建路径
            if image_url.startswith('/'):
                image_url = image_url[1:]  # 移除开头的斜杠
            # 确保使用正确的路径分隔符
            image_url = image_url.replace('/', os.path.sep)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_url)
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            print(f"图像文件不存在: {image_path}")
            # 尝试直接使用URL作为路径，确保使用正确的分隔符
            image_path = os.path.join('uploads', 'retinal_images', str(user_id), os.path.basename(image_url).replace('/', os.path.sep))
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"无法找到图像文件: {image_url}")
        
        # 创建保存分割结果的目录
        result_folder = os.path.join('uploads', 'segmentation_results', str(user_id), str(image_id))
        os.makedirs(result_folder, exist_ok=True)
        
        # 更新进度 - 准备阶段完成
        segmentation.progress = 10.0
        db.session.commit()
        
        # 初始化模型
        model = RetinalSegmentationModel()
        
        # 更新进度 - 模型加载完成
        segmentation.progress = 20.0
        db.session.commit()
        
        # 调用模型进行分割
        try:
            
            result_paths = model.segment_image(image_path, result_folder)
                
            # 获取可用模型数量
            available_models = model.available_models if hasattr(model, 'available_models') else []
            total_models = len(available_models) if available_models else 4  # 默认4种模型
            
            # 计算每个模型处理完成后的进度增量
            progress_increment = 70.0 / total_models
            
            # 根据结果路径中的键判断已完成的模型数量
            completed_models = 0
            for lesion_type in ['he', 'ex', 'ma', 'se']:
                if f'{lesion_type}_path' in result_paths and result_paths[f'{lesion_type}_path']:
                    completed_models += 1
                    # 更新进度 - 每完成一个模型更新一次
                    current_progress = 20.0 + completed_models * progress_increment
                    segmentation.progress = min(current_progress, 90.0)  # 确保不超过90%
                    db.session.commit()
                    print(f"分割进度更新: 完成 {lesion_type} 模型, 当前进度 {segmentation.progress:.1f}%")
            
            # 确保最终进度达到90%
            segmentation.progress = 90.0
            db.session.commit()
            print(f"所有模型分割完成，进度更新至: {segmentation.progress:.1f}%")

        except TypeError as e:
            if "pic should be PIL Image or ndarray" in str(e):
                # 如果出现类型错误，尝试手动加载图像并转换格式
                print("尝试手动转换图像格式...")
                # 创建一个简单的图像处理函数
                from core.transform.transforms_group import Compose, Normalize
                
                # 手动加载图像
                import cv2
                img = cv2.imread(image_path)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                result_paths = model.segment_image(img, result_folder)
                segmentation.progress = 90.0
                db.session.commit()
            else:
                raise
        
        # 更新分割结果记录
        base_url = "/uploads/retinal_image/"
        # 使用URL格式的路径（使用正斜杠）
        url_relative_path = '/'.join(['segmentation_results', str(user_id), str(image_id)])

        # 构建URL
        he_url = f"{base_url}{url_relative_path}/{os.path.basename(result_paths.get('he_path', ''))}" if 'he_path' in result_paths else None
        ex_url = f"{base_url}{url_relative_path}/{os.path.basename(result_paths.get('ex_path', ''))}" if 'ex_path' in result_paths else None
        ma_url = f"{base_url}{url_relative_path}/{os.path.basename(result_paths.get('ma_path', ''))}" if 'ma_path' in result_paths else None
        se_url = f"{base_url}{url_relative_path}/{os.path.basename(result_paths.get('se_path', ''))}" if 'se_path' in result_paths else None
        combined_url = f"{base_url}{url_relative_path}/{os.path.basename(result_paths.get('combined_path', ''))}" if 'combined_path' in result_paths else None
        # 更新分割结果记录
        segmentation.he_url = he_url
        segmentation.ex_url = ex_url
        segmentation.ma_url = ma_url
        segmentation.se_url = se_url
        segmentation.combined_url = combined_url
        
        # 记录可用的模型类型
        segmentation.available_models = ','.join(model.available_models) if hasattr(model, 'available_models') else ''
        
        segmentation.process_time = datetime.utcnow()
        segmentation.status = 'completed'
        segmentation.progress = 100.0  # 设置为100%完成
        db.session.commit()
        
        print(f"分割任务完成: image_id={image_id}")
        return True
    
    except Exception as e:
        print(f"分割任务失败: {str(e)}")
        
        # 确保 segmentation 变量已定义
        try:
            # 如果 segmentation 未定义，尝试重新查询
            if 'segmentation' not in locals() or segmentation is None:
                segmentation = SegmentationResult.query.get(segmentation_id)
            
            # 更新状态为失败
            if segmentation:
                segmentation.status = 'failed'
                segmentation.error_message = str(e)
                db.session.commit()
        except Exception as inner_e:
            print(f"更新分割状态失败: {str(inner_e)}")

    finally:
        # 如果创建了上下文，需要在最后弹出
        if ctx:
            try:
                ctx.pop()
            except Exception as e:
                print(f"弹出上下文失败: {str(e)}")
