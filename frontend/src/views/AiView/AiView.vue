<template>
  <div class="container">
    <h1 class="title">Upload Image and Ask a Question</h1>

    <!-- Prompt Section -->
    <div class="prompt-section">
      <h2 class="prompt-title">How to Use This Tool</h2>
      <div class="prompt-content">
        <p>1. Enter your question in the text box below</p>
        <p>2. Upload either a single image or multiple images</p>
        <p>3. Click Submit to get your answer</p>
        <p>4. View the response below the preview section</p>
      </div>
    </div>

    <form @submit.prevent="submitForm" class="form">
      <div class="form-group">
        <label for="question">Question:</label>
        <input type="text" v-model="question" id="question" placeholder="Enter your question" class="input">
      </div>

      <div class="form-group">
        <label for="images">Upload one or more images:</label>
        <input type="file" @change="handleFileChange" id="images" accept="image/*" multiple class="file-input">
      </div>

      <button type="submit" class="submit-button" :disabled="isSubmitting">
        {{ isSubmitting ? 'Submitting...' : 'Submit' }}
      </button>
    </form>

    <!-- Optional UI loading message -->
    <p v-if="isSubmitting" class="loading-message">Submitting your request, please wait...</p>

    <!-- Image Preview -->
    <div class="preview-section" v-if="previewImage || previewImages.length">
      <h2 class="preview-title">Image Preview</h2>
      <div class="preview-wrapper">
        <img v-if="previewImage" :src="previewImage" class="preview-image" alt="Single Image Preview">
        <img v-for="(img, index) in previewImages" :key="index" :src="img" class="preview-image" alt="Multiple Images Preview">
      </div>
    </div>

    <!-- Render Response -->
    <transition name="fade">
      <div v-if="response" class="response-card">
        <h3 class="response-title">Response:</h3>
        <div v-html="renderedMarkdown" class="markdown-content"></div>
        <p v-if="response.error" class="error">Error: {{ response.error }}</p>
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
      isSubmitting: false, // 控制按钮状态
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
      const files = Array.from(event.target.files);
      this.selectedImages = files;

      if (files.length === 1) {
        this.selectedImage = files[0];
        this.previewImage = URL.createObjectURL(files[0]);
        this.previewImages = [];
      } else if (files.length > 1) {
        this.selectedImage = null;
        this.previewImage = null;
        this.previewImages = files.map(file => URL.createObjectURL(file));
      } else {
        this.selectedImage = null;
        this.previewImage = null;
        this.previewImages = [];
      }
    },
    async submitForm() {
      if (this.isSubmitting) return;

      this.isSubmitting = true;
      this.response = null;

      const formData = new FormData();
      formData.append('question', this.question);

      if (this.selectedImage) {
        formData.append('image', this.selectedImage);
      }

      if (this.selectedImages.length > 1) {
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
        this.response = { error: error.response?.data?.error || 'Request Failed' };
      } finally {
        this.isSubmitting = false;
      }
    },
  },
};
</script>

<style scoped>
:root {
  --primary-color: #ffffff;
  --primary-light: #f0f2f5;
  --primary-dark: #333333;
  --accent-color: #79459c;
  --border-radius: 12px;
  --box-shadow: rgba(0, 0, 0, 0.1);
  --input-border: #ccc;
  --input-focus: #9f5cc0;
}

.container {
  max-width: 1370px;
  margin: 40px auto;
  padding: 40px;
  background: var(--primary-light);
  border-radius: var(--border-radius);
  box-shadow: 0 4px 20px var(--box-shadow);
}

.title {
  text-align: center;
  font-size: 36px;
  color: var(--primary-dark);
  margin-bottom: 20px;
}

.prompt-section {
  background-color: #e8eaf6;
  padding: 20px;
  border-radius: var(--border-radius);
  margin-bottom: 30px;
  border-left: 5px solid var(--accent-color);
}

.prompt-title {
  font-size: 22px;
  color: var(--primary-dark);
  margin-bottom: 15px;
}

.prompt-content {
  font-size: 16px;
  line-height: 1.6;
  color: #555;
}

.prompt-content p {
  margin: 8px 0;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

label {
  font-size: 16px;
  color: var(--primary-dark);
  margin-bottom: 8px;
  font-weight: 500;
}

.input, .file-input {
  padding: 12px;
  font-size: 16px;
  border: 2px solid var(--input-border);
  border-radius: var(--border-radius);
  background-color: var(--primary-color);
  transition: all 0.3s ease;
}

.input:focus, .file-input:focus {
  border-color: var(--input-focus);
  outline: none;
  box-shadow: 0 0 0 3px rgba(92, 107, 192, 0.2);
}

.submit-button {
  padding: 14px;
  background-color: var(--accent-color);
  color: #cdb8d1;
  border: none;
  border-radius: var(--border-radius);
  font-size: 18px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.submit-button:hover {
  background-color: #a239ab;
  transform: translateY(-2px);
}

.submit-button:disabled {
  background-color: #b59bc4;
  cursor: not-allowed;
}

.loading-message {
  color: #555;
  font-size: 16px;
  margin-top: 12px;
}

.preview-section {
  margin-top: 40px;
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
  gap: 24px;
  justify-content: center;
}

.preview-image {
  width: 280px;
  height: 200px;
  object-fit: cover;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px var(--box-shadow);
  border: 2px solid var(--input-border);
}

.response-card {
  margin-top: 40px;
  padding: 24px;
  background: #ffffff;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px var(--box-shadow);
  border: 1px solid var(--input-border);
}

.response-title {
  font-size: 24px;
  color: var(--primary-dark);
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
  background: #f0f2f5;
  padding: 2px 4px;
  border-radius: 4px;
}

.markdown-content pre {
  background: #f0f2f5;
  padding: 10px;
  border-radius: 8px;
  overflow-x: auto;
}

.error {
  font-size: 18px;
  color: #e74c3c;
  margin-top: 10px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
