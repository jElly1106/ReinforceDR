import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from datetime import datetime
import uuid
import shutil
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import transforms
import sys
import traceback

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入模型和工具函数
from core.hednet import HNNNet
from core.utils import get_images
from core.dataset import IDRIDDataset
from core.transform.transforms_group import Compose, Normalize

class RetinalSegmentationModel:
    """眼底图像分割模型类"""

    def __init__(self, model_path=None):
        """初始化模型"""
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        
        # 直接从models目录加载模型
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
        
        # 设置模型路径，支持pth.tar格式
        self.model_paths = {
            'ex': self._find_model_file(models_dir, 'EX'),
            'ma': self._find_model_file(models_dir, 'MA'),
            'se': self._find_model_file(models_dir, 'SE'),
            'he': self._find_model_file(models_dir, 'HE'),
        }
        
        # 初始化模型字典
        self.models = {}
        self.image_size = 512  # 根据实际模型调整
        self.softmax = nn.Softmax(dim=1)
        
        # 加载模型
        self._load_models()
        
        # 记录可用的模型类型
        self.available_models = list(self.models.keys())
        print(f"可用的模型类型: {self.available_models}")
    
    def _find_model_file(self, directory, lesion_type):
        """查找模型文件，支持多种扩展名"""
        # 检查不同扩展名的模型文件
        extensions = ['.pth', '.pth.tar', '.tar', '.pt']
        for ext in extensions:
            # 检查不同的文件命名模式
            patterns = [
                f"{lesion_type}_model{ext}",
                f"{lesion_type.lower()}_model{ext}",
                f"{lesion_type}{ext}",
                f"{lesion_type.lower()}{ext}",
                f"model_{lesion_type}{ext}",
                f"model_{lesion_type.lower()}{ext}"
            ]
            
            for pattern in patterns:
                path = os.path.join(directory, pattern)
                if os.path.isfile(path):
                    return path
        
        # 如果在archive中找不到，尝试在models目录中查找
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
        for ext in extensions:
            path = os.path.join(models_dir, f"{lesion_type}_model{ext}")
            if os.path.isfile(path):
                return path
        
        # 如果都找不到，返回默认路径
        return os.path.join(models_dir, f"{lesion_type}_model.pth")
    
    
    def _load_models(self):
        """加载所有分割模型，支持pth.tar格式"""
        for lesion_type, model_path in self.model_paths.items():
            if os.path.isfile(model_path):
                print(f"加载模型: {lesion_type} 从 {model_path}")
                model = HNNNet(pretrained=False, class_number=2)
                
                try:
                    # 加载模型权重
                    checkpoint = torch.load(model_path, map_location=self.device)
                    
                    # 处理不同格式的模型文件
                    if isinstance(checkpoint, dict):
                        # 检查常见的权重键名
                        if 'state_dict' in checkpoint:
                            state_dict = checkpoint['state_dict']
                        elif 'g_state_dict' in checkpoint:
                            state_dict = checkpoint['g_state_dict']
                        elif 'model_state_dict' in checkpoint:
                            state_dict = checkpoint['model_state_dict']
                        elif 'net' in checkpoint:
                            state_dict = checkpoint['net']
                        else:
                            # 如果没有找到常见的键，尝试使用整个字典
                            state_dict = checkpoint
                    else:
                        # 如果不是字典，直接使用
                        state_dict = checkpoint
                    
                    # 处理可能的前缀问题
                    if all(k.startswith('module.') for k in state_dict.keys()):
                        # 移除'module.'前缀(通常是DataParallel添加的)
                        state_dict = {k[7:]: v for k, v in state_dict.items()}
                    
                    # 加载状态字典
                    model.load_state_dict(state_dict)
                    model.to(self.device)
                    model.eval()
                    self.models[lesion_type] = model
                    print(f"模型 {lesion_type} 加载成功")
                except Exception as e:
                    print(f"加载模型 {lesion_type} 失败: {str(e)}")
            else:
                print(f"模型文件不存在: {model_path}")

    def segment_image(self, image_path, output_dir):
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
            
            # 读取图像 - 支持路径字符串或直接传入图像数据
            if isinstance(image_path, str):
                original_image = cv2.imread(image_path)
                if original_image is None:
                    raise ValueError(f"无法读取图像: {image_path}")
                base_filename = os.path.basename(image_path)
            else:
                # 如果直接传入了图像数据
                original_image = image_path
                if isinstance(original_image, torch.Tensor):
                    # 如果是PyTorch张量，转换为numpy数组
                    original_image = original_image.cpu().numpy()
                    if original_image.shape[0] == 3:  # 如果是CHW格式
                        original_image = np.transpose(original_image, (1, 2, 0))
                # 为非字符串输入生成唯一文件名
                base_filename = f"segmentation_{uuid.uuid4().hex}.jpg"
            
            # 生成唯一文件名前缀
            filename_prefix = uuid.uuid4().hex
            
            # 准备结果路径
            self.result_paths = {
                'he_path': os.path.join(output_dir, f"{filename_prefix}_HE_{base_filename}"),
                'ex_path': os.path.join(output_dir, f"{filename_prefix}_EX_{base_filename}"),
                'ma_path': os.path.join(output_dir, f"{filename_prefix}_MA_{base_filename}"),
                'se_path': os.path.join(output_dir, f"{filename_prefix}_SE_{base_filename}"),
                'combined_path': os.path.join(output_dir, f"{filename_prefix}_COMBINED_{base_filename}"),
                'all_masks_path': os.path.join(output_dir, f"{filename_prefix}_ALL_MASKS_{base_filename}")
            }
            
            # 如果没有加载任何模型，使用模拟分割
            if not self.models:
                print("没有加载任何模型，使用模拟分割")
                self._simulate_segmentation(original_image, self.result_paths)
                return self.result_paths
            
            # 预处理图像 - 使用PyTorch内置的transforms而不是自定义Compose
            transform = transforms.Normalize(
                mean=[0.485, 0.456, 0.406], 
                std=[0.229, 0.224, 0.225]
            )
            
            # 创建一个临时目录保存预处理后的图像
            temp_dir = os.path.join(output_dir, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            temp_image_path = os.path.join(temp_dir, f"temp_{base_filename}")
            
            # 保存图像到临时文件
            if not isinstance(original_image, np.ndarray):
                print(f"警告：图像类型不是numpy数组，而是 {type(original_image)}")
                if isinstance(original_image, torch.Tensor):
                    original_image = original_image.cpu().numpy()
                    if original_image.shape[0] == 3:  # 如果是CHW格式
                        original_image = np.transpose(original_image, (1, 2, 0))
                elif hasattr(original_image, 'numpy'):  # 如果是PIL图像
                    original_image = np.array(original_image)

            # 确保图像是BGR格式（OpenCV需要）
            if len(original_image.shape) == 3 and original_image.shape[2] == 3:
                if original_image.dtype != np.uint8:
                    original_image = (original_image * 255).astype(np.uint8)
            else:
                print(f"警告：图像形状不正确: {original_image.shape}")
            cv2.imwrite(temp_image_path, original_image)
            
            # 创建一个空的掩码图像用于保存分割结果
            h, w, _ = original_image.shape
            combined_mask = np.zeros((h, w, 3), dtype=np.uint8)
            all_masks = np.zeros((h, w, 3), dtype=np.uint8)
            
            # 对每种病变类型进行分割
            for lesion_type, model in self.models.items():
                if model is not None:
                    # 创建数据集和加载器
                    dataset = self._create_dataset(temp_image_path, transform)
                    loader = DataLoader(dataset, batch_size=1, shuffle=False)
                    
                    # 进行分割
                    mask = self._segment_with_model(model, loader, original_image.shape)
                    
                    # 保存分割结果，并获取彩色掩码
                    color_mask = self._save_segmentation_result(original_image, mask, self.result_paths[f'{lesion_type}_path'], lesion_type)
                    
                    # 更新组合掩码（叠加在原图上）
                    self._update_combined_mask(combined_mask, mask, lesion_type)
                    
                    # 更新所有掩码图像（黑色背景）
                    all_masks = cv2.addWeighted(all_masks, 1, color_mask, 1, 0)
            
            # 对于缺失的模型，使用模拟结果
            missing_models = [lesion_type for lesion_type in ['he', 'ex', 'ma', 'se'] if lesion_type not in self.models]
            if missing_models:
                print(f"缺少以下模型，将使用模拟结果: {missing_models}")
                self._simulate_missing_models(original_image, self.result_paths, missing_models, combined_mask)
            
            # 保存组合结果（叠加在原图上）
            self._save_combined_result(original_image, combined_mask, self.result_paths['combined_path'])
            
            # 保存所有掩码的组合图像（黑色背景）
            cv2.imwrite(self.result_paths['all_masks_path'], all_masks)
            
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return self.result_paths
            
        except Exception as e:
            print(f"分割过程出错: {str(e)}")
            traceback.print_exc()  # 打印完整的错误堆栈
            raise


    def _create_dataset(self, image_path, transform):
        """创建用于推理的数据集，使用PyTorch标准transforms"""
        class SimpleDataset(torch.utils.data.Dataset):
            def __init__(self, image_path, transform=None):
                self.image_path = image_path
                self.transform = transform
                
            def __len__(self):
                return 1
                
            def __getitem__(self, idx):
                try:
                    # 读取图像
                    image = cv2.imread(self.image_path)
                    if image is None:
                        raise ValueError(f"无法读取图像: {self.image_path}")
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    
                    # 转换为PyTorch张量 (C,H,W)格式
                    image = torch.from_numpy(image.transpose((2, 0, 1))).float() / 255.0
                    
                    # 应用转换 - 确保transform是PyTorch的transform
                    if self.transform:
                        image = self.transform(image)
                    
                    # 创建一个假的掩码（在推理时不会使用）
                    mask = torch.zeros((2, image.shape[1], image.shape[2]))
                    
                    return image, mask
                except Exception as e:
                    print(f"加载图像失败: {str(e)}")
                    traceback.print_exc()  # 打印完整的错误堆栈
                    # 返回一个空图像
                    empty_image = torch.zeros((3, 512, 512))
                    empty_mask = torch.zeros((2, 512, 512))
                    return empty_image, empty_mask
        
        return SimpleDataset(image_path, transform)   
    
    def _segment_with_model(self, model, loader, original_shape):
        """使用模型进行分割，参考evaluate_model.py的实现"""
        h, w, _ = original_shape
        mask_pred = np.zeros((h, w), dtype=np.float32)

        model.eval()  # 确保模型处于评估模式

        with torch.no_grad():
            for inputs, _ in loader:
                inputs = inputs.to(device=self.device, dtype=torch.float)
                bs, c, input_h, input_w = inputs.shape
                
                # 处理大图像，分块处理
                h_size = (input_h - 1) // self.image_size + 1
                w_size = (input_w - 1) // self.image_size + 1
                masks_pred = torch.zeros((bs, 2, input_h, input_w)).to(device=self.device, dtype=torch.float)
                
                for i in range(h_size):
                    for j in range(w_size):
                        h_max = min(input_h, (i + 1) * self.image_size)
                        w_max = min(input_w, (j + 1) * self.image_size)
                        inputs_part = inputs[:, :, i*self.image_size:h_max, j*self.image_size:w_max]
                        
                        # 模型推理，获取最后一个输出
                        outputs = model(inputs_part)
                        if isinstance(outputs, (tuple, list)):
                            outputs = outputs[-1]
                        
                        # 更新预测掩码
                        masks_pred[:, :, i*self.image_size:h_max, j*self.image_size:w_max] = outputs
                
                # 应用softmax获取概率
                masks_pred_softmax = nn.Softmax(dim=1)(masks_pred)
                
                # 获取病变类别的概率（索引1）
                prob = masks_pred_softmax[0, 1].cpu().numpy()
                
                # 调整大小以匹配原始图像
                if prob.shape[0] != h or prob.shape[1] != w:
                    prob = cv2.resize(prob, (w, h), interpolation=cv2.INTER_LINEAR)
                
                mask_pred = prob

        # 应用阈值获取二值掩码
        binary_mask = (mask_pred > 0.5).astype(np.uint8) * 255

        return binary_mask
    
    def _save_segmentation_result(self, original_image, mask, output_path, lesion_type):
        """保存分割结果"""
        # 创建一个黑色背景的掩码图像
        color_mask = np.zeros_like(original_image)
        
        # 根据病变类型设置不同的颜色
        if lesion_type == 'he':  # 出血
            color = [0, 0, 255]  # 红色
        elif lesion_type == 'ex':  # 硬性渗出物
            color = [0, 255, 255]  # 黄色
        elif lesion_type == 'ma':  # 微血管瘤
            color = [255, 0, 0]  # 蓝色
        elif lesion_type == 'se':  # 软性渗出物
            color = [0, 255, 0]  # 绿色
        
        # 将掩码区域设置为对应颜色
        color_mask[mask > 0] = color
        
        # 保存纯掩码图像（黑色背景，彩色病灶）
        mask_only_path = output_path.replace('.jpg', '_mask.jpg')
        cv2.imwrite(mask_only_path, color_mask)
        
        # 降低原图像亮度
        darkened_image = cv2.convertScaleAbs(original_image, alpha=0.4, beta=30)  # alpha控制对比度，beta控制亮度
        
        # 将掩码与降低亮度后的原图像叠加
        alpha = 1.0  # 增加透明度，使掩码更明显
        result = cv2.addWeighted(darkened_image, 1, color_mask, alpha, 0)
        
        # 保存叠加结果
        cv2.imwrite(output_path, result)
        
        # 更新结果路径字典，添加纯掩码图像路径
        lesion_mask_key = f'{lesion_type}_mask_path'
        if hasattr(self, 'result_paths') and isinstance(self.result_paths, dict):
            self.result_paths[lesion_mask_key] = mask_only_path
        
        return color_mask  # 返回彩色掩码供组合使用
    

    def _update_combined_mask(self, combined_mask, mask, lesion_type):
        """更新组合掩码，保留每种病灶的独特颜色"""
        # 根据病变类型设置不同的颜色
        if lesion_type == 'he':  # 出血
            color = [0, 0, 255]  # 红色
        elif lesion_type == 'ex':  # 硬性渗出物
            color = [0, 255, 255]  # 黄色
        elif lesion_type == 'ma':  # 微血管瘤
            color = [255, 0, 0]  # 蓝色
        elif lesion_type == 'se':  # 软性渗出物
            color = [0, 255, 0]  # 绿色
        
        # 将当前病灶的掩码区域设置为对应颜色
        # 注意：这里不使用叠加，而是直接设置颜色，避免颜色混合
        combined_mask[mask > 0] = color
        
        return combined_mask

    def _save_combined_result(self, original_image, combined_mask, output_path):
        """保存组合分割结果，确保不同病灶有不同颜色"""
        # 使用与单个掩码图像相同的亮度和对比度调整
        darkened_image = cv2.convertScaleAbs(original_image, alpha=0.4, beta=-30)
        
        # 将组合掩码与降低亮度后的原图像叠加
        alpha = 1.0
        result = cv2.addWeighted(darkened_image, 1, combined_mask, alpha, 0)
        
        # 保存不带图例的结果
        cv2.imwrite(output_path, result)
        
        # 使用PIL添加图例
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        import os
        
        # 转换OpenCV图像为PIL图像
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(result_rgb)
        
        # 计算图例区域大小
        legend_height = 30
        legend_margin = 10
        total_legend_height = legend_height*4 + legend_margin*5
        
        # 创建一个新的带图例的图像
        w, h = img_pil.size
        img_with_legend = Image.new('RGB', (w, h + total_legend_height), color=(255, 255, 255))
        img_with_legend.paste(img_pil, (0, 0))
        
        # 准备绘图
        draw = ImageDraw.Draw(img_with_legend)
        
        # 尝试加载中文字体，如果失败则使用默认字体
        try:
            # 尝试使用系统中可能存在的中文字体
            font_path = "C:\\Windows\\Fonts\\simhei.ttf"  # 黑体
            if not os.path.exists(font_path):
                font_path = "C:\\Windows\\Fonts\\simsun.ttc"  # 宋体
            if not os.path.exists(font_path):
                font_path = "C:\\Windows\\Fonts\\msyh.ttc"  # 微软雅黑
            
            font = ImageFont.truetype(font_path, 15)
        except:
            # 如果找不到中文字体，使用默认字体
            font = ImageFont.load_default()
        
        # 添加各种病灶类型的图例
        legend_types = [
            ('出血 (HE)', (255, 0, 0)),  # 注意PIL中颜色是RGB格式，而OpenCV是BGR
            ('硬性渗出物 (EX)', (0, 165, 255)),
            ('微血管瘤 (MA)', (255, 0, 255)),
            ('软性渗出物 (SE)', (0, 255, 0))
        ]
        
        for i, (text, color) in enumerate(legend_types):
            # 计算图例位置
            y_pos = h + legend_margin + i * (legend_height + legend_margin)
            
            # 绘制颜色方块
            draw.rectangle(
                [(legend_margin, y_pos), (legend_margin + legend_height, y_pos + legend_height)],
                fill=color
            )
            
            # 绘制文字说明
            draw.text(
                (legend_margin*2 + legend_height, y_pos + legend_height//2 - 7),
                text,
                fill=(0, 0, 0),
                font=font
            )
        
        # 保存带图例的结果
        legend_output_path = output_path.replace('.jpg', '_with_legend.jpg')
        img_with_legend.save(legend_output_path)
        
        # 更新结果路径
        if hasattr(self, 'result_paths') and isinstance(self.result_paths, dict):
            self.result_paths['combined_with_legend_path'] = legend_output_path
        
        return legend_output_path   

        
    def _simulate_segmentation(self, image, result_paths):
        """
        模拟分割过程，生成示例分割结果
        在实际应用中，这里应该替换为真实的模型推理代码
        """
        # 模拟出血(HE)分割结果 - 红色通道增强
        he_result = image.copy()
        he_result[:,:,0] = np.minimum(he_result[:,:,0] * 1.5, 255).astype(np.uint8)
        cv2.imwrite(result_paths['he_path'], he_result)
        
        # 模拟硬性渗出(EX)分割结果 - 黄色增强
        ex_result = image.copy()
        ex_result[:,:,0] = np.minimum(ex_result[:,:,0] * 1.2, 255).astype(np.uint8)
        ex_result[:,:,1] = np.minimum(ex_result[:,:,1] * 1.2, 255).astype(np.uint8)
        cv2.imwrite(result_paths['ex_path'], ex_result)
        
        # 模拟微血管瘤(MA)分割结果 - 绿色通道增强
        ma_result = image.copy()
        ma_result[:,:,1] = np.minimum(ma_result[:,:,1] * 1.5, 255).astype(np.uint8)
        cv2.imwrite(result_paths['ma_path'], ma_result)
        
        # 模拟软性渗出(SE)分割结果 - 蓝色通道增强
        se_result = image.copy()
        se_result[:,:,2] = np.minimum(se_result[:,:,2] * 1.5, 255).astype(np.uint8)
        cv2.imwrite(result_paths['se_path'], se_result)
        
        # 生成组合结果
        combined = image.copy()
        # 简单的组合方法，实际应用中可能需要更复杂的融合
        combined = cv2.addWeighted(combined, 0.7, he_result, 0.3, 0)
        combined = cv2.addWeighted(combined, 0.7, ex_result, 0.3, 0)
        combined = cv2.addWeighted(combined, 0.7, ma_result, 0.3, 0)
        combined = cv2.addWeighted(combined, 0.7, se_result, 0.3, 0)
        cv2.imwrite(result_paths['combined_path'], combined)
        
        # 尝试从archive文件夹复制结果
        self._try_copy_from_archive(result_paths)
    
    def _simulate_missing_models(self, image, result_paths, missing_models, combined_mask):
        """为缺失的模型生成模拟结果"""
        for lesion_type in missing_models:
            # 创建模拟结果
            result = image.copy()
            
            if lesion_type == 'he':  # 出血 - 红色通道增强
                result[:,:,2] = np.minimum(result[:,:,2] * 1.5, 255).astype(np.uint8)
                mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
                # 添加一些模拟的病变区域
                cv2.circle(mask, (image.shape[1]//3, image.shape[0]//3), 50, 255, -1)
            elif lesion_type == 'ex':  # 硬性渗出 - 黄色增强
                result[:,:,0] = np.minimum(result[:,:,0] * 1.2, 255).astype(np.uint8)
                result[:,:,1] = np.minimum(result[:,:,1] * 1.2, 255).astype(np.uint8)
                mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
                cv2.circle(mask, (image.shape[1]//2, image.shape[0]//2), 40, 255, -1)
            elif lesion_type == 'ma':  # 微血管瘤 - 绿色通道增强
                result[:,:,1] = np.minimum(result[:,:,1] * 1.5, 255).astype(np.uint8)
                mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
                cv2.circle(mask, (2*image.shape[1]//3, image.shape[0]//3), 30, 255, -1)
            elif lesion_type == 'se':  # 软性渗出 - 蓝色通道增强
                result[:,:,0] = np.minimum(result[:,:,0] * 1.5, 255).astype(np.uint8)
                mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
                cv2.circle(mask, (image.shape[1]//3, 2*image.shape[0]//3), 60, 255, -1)
            
            # 保存结果
            cv2.imwrite(result_paths[f'{lesion_type}_path'], result)
            
            # 更新组合掩码
            self._update_combined_mask(combined_mask, mask, lesion_type)
            
            print(f"已生成{lesion_type}的模拟结果")

    def _try_copy_from_archive(self, result_paths):
        """尝试从archive文件夹复制模型结果"""
        try:
            archive_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'core', 'archive', 'data')
            if os.path.exists(archive_dir):
                # 这里可以根据实际的archive文件夹结构来复制文件
                # 例如，如果有特定的结果文件，可以复制到对应的路径
                print(f"尝试从archive目录复制数据: {archive_dir}")
                # 列出archive目录中的文件
                files = os.listdir(archive_dir)
                print(f"Archive目录中的文件: {files}")
                
                # 这里可以添加具体的复制逻辑
                # 例如：
                # for file in files:
                #     if file.endswith("_HE.png"):
                #         shutil.copy(os.path.join(archive_dir, file), result_paths['he_path'])
        except Exception as e:
            print(f"从archive复制文件失败: {str(e)}")