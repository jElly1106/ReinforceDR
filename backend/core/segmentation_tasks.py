import os
from datetime import datetime
from common.extensions import db
from database.models import RetinalImage, SegmentationResult
from flask import current_app
from PIL import Image
import numpy as np
import time
import requests
import tempfile
import zipfile
import io
import uuid
import shutil
import traceback

def process_segmentation(image_id, segmentation_id, model_name, app=None):
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
        
        # 记录可用的模型类型
        segmentation.available_models = model_name

        # 更新状态为处理中
        segmentation.status = 'processing'
        segmentation.progress = 0.0
        db.session.commit()
    
        # 获取图像URL并转换为本地路径
        image_url = image.image_url
        user_id = image.uploaded_by
                
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
            image_path = os.path.join('uploads', 'retinal','images', str(user_id), os.path.basename(image_url).replace('/', os.path.sep))
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"无法找到图像文件: {image_url}")
        
        # 创建保存分割结果的目录
        result_folder = os.path.join('uploads', 'segmentation_results', str(user_id), str(image_id))
        os.makedirs(result_folder, exist_ok=True)
   
        # 调用外部服务模型进行分割
        result_paths = segment_image(image_path, result_folder, model_name)
        
        # 更新分割结果记录
        base_url = "/api/retinal/image/"
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

def segment_image(image_path, output_dir, model_name):
    """
    对眼底图像进行分割
    
    Args:
        image_path: 原始图像路径或图像数据
        output_dir: 输出目录
        
    Returns:
        dict: 包含各种分割结果路径的字典
    """
    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 调用外部服务获取分割结果
        external_service_url = ""
        if model_name == "hednet":
            external_service_url = "http://localhost:6004/detect"
        elif model_name == "m2mrf":
            external_service_url = "http://localhost:6005/detect"
        elif model_name == "unet":
            external_service_url = "http://localhost:6006/detect"
        else:
            raise ValueError(f"不支持的模型名称：{model_name}")
        
        with open(image_path, 'rb') as f:
            files = {'image': ("test", f, 'image/jpeg')}
            response = requests.post(external_service_url, files=files, timeout=300)  # 超时5分钟
            
        if response.status_code != 200:
            raise Exception(f"外部服务调用失败，状态码：{response.status_code}")

        # debug:是否传递结果
        zip_save_path = os.path.join(output_dir, "segmentation_results.zip")  # 临时目录保存ZIP
        with open(zip_save_path, 'wb') as zip_file:
            zip_file.write(response.content)  # 写入本地文件
            
        # 解析外部服务返回的ZIP文件
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_buffer = io.BytesIO(response.content)
            with zipfile.ZipFile(zip_buffer, 'r') as zipf:
                zipf.extractall(temp_dir)  
                
                result_paths = {
                    'he_path': os.path.join(temp_dir, 'HE.jpg'),
                    'ex_path': os.path.join(temp_dir, 'EX.jpg'),
                    'ma_path': os.path.join(temp_dir, 'MA.jpg'),
                    'se_path': os.path.join(temp_dir, 'SE.jpg'),
                    'combined_path': os.path.join(temp_dir, 'label.png')
                }

                # 保存分割结果到本地
                saved_paths = {}
                for key, path in result_paths.items():
                    if os.path.exists(path):
                        _, ext = os.path.splitext(os.path.basename(path))
                        saved_filename = f"{uuid.uuid4().hex}{ext}"
                        saved_path = os.path.join(output_dir, saved_filename)
                        shutil.move(path, saved_path) 
                        saved_paths[key] = saved_path        
                                
        return saved_paths
        
    except Exception as e:
        print(f"分割过程出错: {str(e)}")
        traceback.print_exc()  # 打印完整的错误堆栈
        raise

def process(segmentation_id):
    segmentation = SegmentationResult.query.get(segmentation_id)

    if not segmentation:
        print(f"找不到分割记录:segmentation_id={segmentation_id}")
        return

    model_name = segmentation.available_models

    external_service_url = ""
    if model_name == "hednet":
        external_service_url = "http://localhost:6004/process"
    elif model_name == "m2mrf":
        external_service_url = "http://localhost:6005/process"
    elif model_name == "unet":
        external_service_url = "http://localhost:6006/process"
    else:
        raise ValueError(f"不支持的模型名称：{model_name}")
    
    response = requests.get(external_service_url, timeout=300)
    return response.process, response.status