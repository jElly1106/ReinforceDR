<template>
  <div class="container">
    <h1 class="title">上传图片并提问</h1>

    <form @submit.prevent="submitForm" class="form">
      <div class="form-group">
        <label for="question">问题:</label>
        <input type="text" v-model="question" id="question" placeholder="请输入你的问题" class="input">
      </div>

      <div class="form-group">
        <label for="image">选择单张图片:</label>
        <input type="file" @change="handleFileChange" id="image" accept="image/*" class="file-input">
      </div>

      <div class="form-group">
        <label for="images">选择多张图片:</label>
        <input type="file" @change="handleMultipleFileChange" id="images" accept="image/*" multiple class="file-input">
      </div>

      <button type="submit" class="submit-button">提交</button>
    </form>

    <!-- 图片预览 -->
    <div class="preview-section" v-if="previewImage || previewImages.length">
      <h2 class="preview-title">图片预览</h2>

      <div class="preview-wrapper">
        <img v-if="previewImage" :src="previewImage" class="preview-image" alt="单张图片预览">
        <img v-for="(img, index) in previewImages" :key="index" :src="img" class="preview-image" alt="多张图片预览">
      </div>
    </div>

    <!-- 渲染返回结果 -->
    <transition name="fade">
      <div v-if="response" class="response-card">
        <h3 class="response-title">返回结果:</h3>
        <div v-html="renderedMarkdown" class="markdown-content"></div>
        <p v-if="response.error" class="error">错误: {{ response.error }}</p>
      </div>
    </transition>
  </div>
</template>
<script>
import API from '../../router/axios';
import { marked } from 'marked';

export default {
  data() {
    return {
      question: '',
      selectedImage: null,
      selectedImages: [],
      response: null,
      previewImage: null,
      previewImages: [],
    };
  },
  computed: {
    renderedMarkdown() {
      if (this.response && this.response.result) {
        return marked(this.response.result);
      }
      return '';
    },
  },
  methods: {
    handleFileChange(event) {
      const file = event.target.files[0];
      this.selectedImage = file;
      if (file) {
        this.previewImage = URL.createObjectURL(file);
      } else {
        this.previewImage = null;
      }
    },
    handleMultipleFileChange(event) {
      const files = Array.from(event.target.files);
      this.selectedImages = files;
      this.previewImages = files.map(file => URL.createObjectURL(file));
    },
    async submitForm() {
      const formData = new FormData();
      formData.append('question', this.question);

      if (this.selectedImage) {
        formData.append('image', this.selectedImage);
      }

      if (this.selectedImages.length > 0) {
        for (let i = 0; i < this.selectedImages.length; i++) {
          formData.append('images[]', this.selectedImages[i]);
        }
      }

      try {
        const response = await API.post('/api/llm/multimodal', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        this.response = response.data;
      } catch (error) {
        this.response = { error: error.response?.data?.error || '请求失败' };
      }
    },
  },
};
</script>
<style scoped>
/* 主体颜色 */
:root {
  --primary-color: #7D5BA6;
  --primary-light: #b89cd7;
  --primary-dark: #5c3c7d;
}

.container {
  max-width: 1100px;
  margin: 40px auto;
  padding: 30px;
  background: rgb(187, 181, 196);
  border-radius: 16px;
  box-shadow: 0 8px 16px rgba(125, 91, 166, 0.2);
}

.title {
  text-align: center;
  font-size: 32px;
  color: var(--primary-dark);
  margin-bottom: 20px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.input, .file-input {
  padding: 12px;
  font-size: 16px;
  border: 2px solid var(--primary-light);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.input:focus, .file-input:focus {
  border-color: var(--primary-dark);
  outline: none;
}

.submit-button {
  padding: 14px;
  background-color: var(--primary-color);
  color: rgb(146, 17, 143);
  border: none;
  border-radius: 10px;
  font-size: 18px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.submit-button:hover {
  background-color: var(--primary-dark);
}

/* 图片预览 */
.preview-section {
  margin-top: 30px;
}

.preview-title {
  text-align: center;
  font-size: 24px;
  color: var(--primary-dark);
  margin-bottom: 20px;
}

.preview-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
}

.preview-image {
  width: 260px;
  height: 180px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(125, 91, 166, 0.3);
}

/* 返回结果样式 */
.response-card {
  margin-top: 40px;
  padding: 24px;
  background: #817c87;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(125, 91, 166, 0.1);
}

.response-title {
  font-size: 24px;
  color: var(--primary-color);
  margin-bottom: 16px;
}

.markdown-content {
  color: #444;
  line-height: 1.7;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3 {
  color: var(--primary-dark);
}

.markdown-content code {
  background: #807b7f;
  padding: 2px 4px;
  border-radius: 4px;
}

.markdown-content pre {
  background: #e7dbe6;
  padding: 10px;
  border-radius: 8px;
  overflow-x: auto;
}

/* 错误信息 */
.error {
  font-size: 18px;
  color: #e74c3c;
  margin-top: 10px;
}

/* 动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
