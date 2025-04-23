from flask import Blueprint, request, jsonify
from common.api_integration import encode_image
from openai import OpenAI

llm_bp = Blueprint('llm', __name__)


@llm_bp.route('/multimodal', methods=['POST'])
def multimodal_conversation_call():
    try:
        # 获取问题文本
        question = request.form.get('question', "请描述这些图片")
        
        # 检查是否有图片文件
        if 'image' not in request.files and 'images[]' not in request.files:
            return jsonify({"error": "没有提供图片文件"}), 400
        
        # 处理消息内容
        message_content = [{"type": "text", "text": question}]
        
        # 处理单张图片上传
        if 'image' in request.files:
            file = request.files['image']
            if file:
                base64_image = encode_image(file)
                message_content.append({
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                })
        
        # 处理多张图片上传
        if 'images[]' in request.files:
            files = request.files.getlist('images[]')
            for file in files:
                if file:
                    base64_image = encode_image(file)
                    message_content.append({
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    })
        
        # 如果没有有效图片，返回错误
        if len(message_content) <= 1:
            return jsonify({"error": "没有提供有效的图片文件"}), 400
        
        client = OpenAI(
            api_key='sk-743310c7aba34b97b9ce13cca22eb31c',
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
        completion = client.chat.completions.create(
            model="qwen2.5-vl-32b-instruct",
            messages=[{"role": "user", "content": message_content}]
        )
        
        # 返回解读结果
        return jsonify({"result": completion.choices[0].message.content})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@llm_bp.route('/multimodal/batch', methods=['POST'])
def batch_multimodal_conversation():
    try:
        # 获取问题文本
        question = request.form.get('question', "请分析这些图片")
        
        # 检查是否有图片文件
        if 'images[]' not in request.files:
            return jsonify({"error": "没有提供图片文件"}), 400
        
        files = request.files.getlist('images[]')
        if not files:
            return jsonify({"error": "没有提供有效的图片文件"}), 400
        
        # 处理消息内容
        message_content = [{"type": "text", "text": question}]
        
        # 处理所有图片
        for file in files:
            if file:
                base64_image = encode_image(file)
                message_content.append({
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                })
        
        client = OpenAI(
            api_key='sk-743310c7aba34b97b9ce13cca22eb31c',
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
        completion = client.chat.completions.create(
            model="qwen2.5-vl-32b-instruct",
            messages=[{"role": "user", "content": message_content}]
        )
        
        # 返回解读结果
        return jsonify({"result": completion.choices[0].message.content})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500