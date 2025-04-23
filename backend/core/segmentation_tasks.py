import os
from datetime import datetime
from common.extensions import db
from database.models import RetinalImage, SegmentationResult
from core.segmentation_model import RetinalSegmentationModel
from flask import current_app
import torch
from PIL import Image
import numpy as np

# def process_segmentation(image_id, segmentation_id):
#     """
#     处理眼底图像分割的任务
    
#     Args:
#         image_id: 图像ID
#         segmentation_id: 分割结果ID
#     """
#     try:
#         # 获取图像和分割记录
#         image = RetinalImage.query.get(image_id)
#         segmentation = SegmentationResult.query.get(segmentation_id)
        
#         if not image or not segmentation:
#             print(f"找不到图像或分割记录: image_id={image_id}, segmentation_id={segmentation_id}")
#             return False
            
#         # 更新状态为处理中
#         segmentation.status = 'processing'
#         db.session.commit()
        
#         # 获取图像路径
#         image_path = image.image_path
        
#         # 创建保存分割结果的目录
#         user_id = image.user_id
#         result_folder = os.path.join('uploads', 'segmentation_results', str(user_id), str(image_id))
#         os.makedirs(result_folder, exist_ok=True)
        
#         # 初始化模型
#         model = RetinalSegmentationModel()
        
#         # 调用模型进行分割
#         result_paths = model.segment_image(image_path, result_folder)
        
#         # 更新分割结果记录
#         segmentation.he_path = result_paths['he_path']
#         segmentation.ex_path = result_paths['ex_path']
#         segmentation.ma_path = result_paths['ma_path']
#         segmentation.se_path = result_paths['se_path']
#         segmentation.combined_path = result_paths['combined_path']
#         segmentation.process_time = datetime.utcnow()
#         segmentation.status = 'completed'
#         db.session.commit()
        
#         print(f"分割任务完成: image_id={image_id}")
#         return True
        
#     except Exception as e:
#         print(f"分割任务失败: {str(e)}")
#         # 发生错误时，更新状态为失败
#         if segmentation:
#             segmentation.status = 'failed'
#             db.session.commit()
#         return False

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
        # 获取图像记录
        from database.models import RetinalImage, SegmentationResult
        from common.extensions import db
        
        image = RetinalImage.query.get(image_id)
        segmentation = SegmentationResult.query.get(segmentation_id)
        
        if not image or not segmentation:
            print(f"找不到图像或分割记录: image_id={image_id}, segmentation_id={segmentation_id}")
            return
        
        # 更新状态为处理中
        segmentation.status = 'processing'
        db.session.commit()
    
        # 获取图像路径
        image_path = image.image_path
        
        # 创建保存分割结果的目录
        user_id = image.user_id
        result_folder = os.path.join('uploads', 'segmentation_results', str(user_id), str(image_id))
        os.makedirs(result_folder, exist_ok=True)
        
        # 初始化模型
        model = RetinalSegmentationModel()
        
        # 调用模型进行分割
        try:
            # 添加类型转换处理
            result_paths = model.segment_image(image_path, result_folder)
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
                
                # 调用修改后的分割方法
                result_paths = model.segment_image(img, result_folder)
            else:
                raise
        
        # 更新分割结果记录
        segmentation.he_path = result_paths.get('he_path', None)
        segmentation.ex_path = result_paths.get('ex_path', None)
        segmentation.ma_path = result_paths.get('ma_path', None)
        segmentation.se_path = result_paths.get('se_path', None)
        segmentation.combined_path = result_paths.get('combined_path', None)
        
        # 记录可用的模型类型
        segmentation.available_models = ','.join(model.available_models) if hasattr(model, 'available_models') else ''
        
        segmentation.process_time = datetime.utcnow()
        segmentation.status = 'completed'
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