<template> 
  <div class="predict-model">
    <BaseStation ref="baseStation" />
    <div class="right-panel">
      <h2 style="font-size: 36px; text-align: left; margin-top: 10px">Predict Model</h2>
      <div class="upload-section">
        <h2 style="text-align: left; margin-top: -10px">Upload Data</h2>
        <h2 style="text-align: left; font-size:16px; margin-top: -10px">Please upload predict data according to the requirements of different types of models.</h2>

        <el-upload
          ref="uploadDom"
          action=""
          v-model:file-list="fileList"
          :auto-upload="false"
          multiple
          drag
          accept=".png,.jpg,.jpeg,.bmp,.tif,.tiff"
          :on-change="handleChange"
          class="uploadElement"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <p style="font-size: 16px; margin-top: -5px;color:black">Drag your file(s) to start uploading</p>
          <div class="upload-dropzone">
            <span class="divider">OR</span>
            <button class="browse-button">Browse files</button>
          </div>
        </el-upload>

        <p class="file-support">Only support 'png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff' files</p>

        <!-- 预览图像 -->
        <div v-if="previewImageUrl && !isSubmitting" class="image-preview">
          <h3 style="text-align: left">Image Preview:</h3>
          <img :src="previewImageUrl" alt="Preview" class="preview-img" />
        </div>

        <!-- 提交按钮 -->
        <div style="text-align: right;">
          <button class="submit-button" @click="submit" :disabled="isSubmitting">Submit</button>
          <div v-if="loading">
            <LoadComponent ref="loadComponent"/>
          </div>
        </div>
      </div>

      <!-- 提交后显示进度条替代预览 -->
      <div class="progress-display" v-if="progress > 0 && progress < 100">
        <p>Processing: {{ progress }}%</p>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
      </div>

      <!-- 预测结果展示 -->
      <div class="result-section" v-show="processed_image_url">
        <p style="margin: 0 auto; height: 30px; width:60%; padding: 20px; background-color: #f0f0f0; color: #333; font-size: 16px; border-radius: 5px; text-align: center; font-weight: bold;">
          Predict Results have been generated.
        </p>
        <div class="result-content">
          <div class="image-container">
            <img :src="currentImageUrl" alt="Processed Image" />
            <div class="download-overlay">
              <button @click="downloadFile">Download Image</button>
            </div>
          </div>
          <div class="lesion-panel">
            <div class="lesion-buttons">
              <button 
                v-for="(lesion, index) in lesions" 
                :key="index"
                @click="showLesion(lesion.type)"
                :class="{ active: currentLesion === lesion.type }"
              >
                {{ lesion.label }}
              </button>
            </div>
            <div class="explanation">
              {{ currentExplanation }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="fixed-left-button">
      <button class="history-button" @click="goToHistory">View model prediction history</button>
    </div>
  </div>
</template>

<script>
import 'element-plus/dist/index.css';
import BaseStation from '../../components/BaseStation.vue';
import LoadComponent from '../../components/LoadComponent.vue';
import API from '../../router/axios';

export default {
  components: { BaseStation, LoadComponent },
  data() {
    return {
      fileList: [],
      previewImageUrl: null,
      isSubmitting: false,
      loading: false,
      progress: 0,
      segmentation_id: 0,
      processed_image_url: null,
      currentImageUrl: null,
      currentLesion: 'combined',
      currentExplanation: 'Combined lesion detection results',
      ex_url: null,
      he_url: null,
      ma_url: null,
      se_url: null,
      lesions: [
        { type: 'combined', label: 'Combined', explanation: 'A comprehensive detection of all types of retinal lesions...' },
        { type: 'ex', label: 'EX', explanation: 'Yellow or white deposits on the retina...' },
        { type: 'he', label: 'HE', explanation: 'Blood leakage from retinal vessels...' },
        { type: 'ma', label: 'MA', explanation: 'Small red dots in the retinal capillary walls...' },
        { type: 'se', label: 'SE', explanation: 'White, fluffy spots caused by ischemic infarction...' }
      ],
      allowedExtensions: ['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'],
    };
  },
  methods: {
    handleChange(file, fileList) {
      const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
      if (!this.allowedExtensions.includes(ext)) {
        this.$message.error(`Unsupported file format: ${ext}`);
        fileList.splice(fileList.indexOf(file), 1);
        return;
      }
      this.fileList = fileList;
      this.previewImageUrl = URL.createObjectURL(file.raw);
      this.$message.success(`File "${file.name}" added successfully.`);
    },

    async submit() {
      if (this.fileList.length === 0) return alert("Please upload a file.");
      if (this.isSubmitting) return alert("Request is already in progress.");

      this.isSubmitting = true;
      this.loading = true;
      this.previewImageUrl = null; // 提交后隐藏预览图

      const formData = new FormData();
      formData.append('file', this.fileList[0].raw);

      try {
        const response = await API.post('/api/retinal/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        this.segmentation_id = response.data.data.segmentation_id;
        this.pollSegmentationResult(this.segmentation_id);
        this.$message.success("Submission successful!");
      } catch (err) {
        this.$message.error("Submission failed.");
        console.error(err);
      } finally {
        this.isSubmitting = false;
        this.loading = false;
      }
    },

    async pollSegmentationResult(id) {
      const interval = setInterval(async () => {
        try {
          const { data } = await API.get(`/api/retinal/segmentation/progress/${id}`);
          if (data.code === 200) {
            this.progress = data.data.progress || 0;

            if (data.data.status === 'completed') {
              clearInterval(interval);
              const result = await API.get(`/api/retinal/segmentation/${id}`);
              if (result.data.code === 200) {
                const d = result.data.data;
                this.processed_image_url = d.combined_url;
                this.ex_url = d.ex_url;
                this.he_url = d.he_url;
                this.ma_url = d.ma_url;
                this.se_url = d.se_url;
                this.currentImageUrl = d.combined_url;
                this.progress = 100;
                setTimeout(() => this.progress = 0, 2000);
              }
            }

            if (data.data.status === 'failed') {
              clearInterval(interval);
              this.progress = 0;
              this.$message.error(`Processing failed: ${data.data.error_message}`);
            }
          }
        } catch (e) {
          console.error("Polling error:", e);
          clearInterval(interval);
          this.progress = 0;
        }
      }, 1000);
    },

    showLesion(type) {
      this.currentLesion = type;
      const lesion = this.lesions.find(l => l.type === type);
      this.currentExplanation = lesion.explanation;
      this.currentImageUrl = this[`${type}_url`] || this.processed_image_url;
    },

    downloadFile() {
      if (!this.currentImageUrl) return this.$message.error("No image to download");
      const a = document.createElement('a');
      a.href = this.currentImageUrl;
      a.download = 'processed_image.png';
      a.click();
    },

    goToHistory() {
      this.$router.push("history");
    },
  }
};
</script>

  
  <style scoped>
  /* 新增进度条样式 */
  .image-preview img.preview-img {
  max-width: 100%;
  max-height: 300px;
  display: block;
  margin-top: 10px;
}
.progress-bar {
  width: 100%;
  background-color: #f3f3f3;
  border-radius: 5px;
  overflow: hidden;
  margin-top: 10px;
  height: 20px;
}
.progress-fill {
  height: 100%;
  background-color: #409EFF;
  transition: width 0.3s ease;
}
  .progress-display {
    margin: 20px 0;
    padding: 15px;
    background: #f5f5f5;
    border-radius: 8px;
  }

  .progress-display p {
    margin: 0 0 10px 0;
    color: #333;
    font-weight: bold;
  }

  .progress-bar {
    height: 10px;
    background: #ddd;
    border-radius: 5px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: #2C2C2C;
    transition: width 0.3s ease;
  }
  .predict-model {
    display: flex;
    height: 100vh;
    font-family: Arial, sans-serif;
    border: 1px solid #E5E5E5;
    margin-left: 35px;
    margin-right: 35px;
    margin-top: 10px;
    margin-bottom: 15px;
    border-radius: 20px;
  }
  
  .left-panel {
    width: 260px;
    padding: 20px;
    background-color: #fCfCfC; 
    display: flex;
    flex-direction: column;
    border-top-left-radius: 20px;
    border-bottom-left-radius: 20px;
  }
  
  .right-panel {
    width: 60%; 
    padding: 20px;
    margin: 0 auto;
  }
  
  .search-input {
    width: 78%;
    padding: 10px;
    margin-top: 5px;
    margin-bottom: 40px;
    margin-left: 20px;
    font-size: 16px;
    border: 1px solid #ddd;
    border-radius: 18px;
    outline: none; 
    transition: border-color 0.2s; 
  }
  
  .search-input:focus {
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
  }
  
  .model-item {
    padding: 12px;
    border-radius: 15px;
    margin-bottom: 15px;
    margin-right: 8px;
    margin-left: 8px;
    cursor: pointer;
    display: flex; 
    flex-direction: column; 
    align-items: flex-start; 
  }
  
  .model-item:hover {
    background-color: #f2f2f2; 
  }
  
  .model-item > div {
    padding-left: 8px; 
  }
  
  .selected-model {
    background-color: #f2f2f2;  
    transition: all 0.1s ease-in-out; 
  }
  .accuracy {
    font-weight: bold;
    margin-top: 5px; 
    color: #535353;
    font-size: 16px; 
  }
  .type {
    font-weight: bold;
    margin-top: 5px; 
    color: #535353;
    font-size: 16px; 
  }
  
  .upload-section {
    padding: 20px;
    margin-top: 0px;
  }
  
  .uploadElement >>> .el-upload-dragger {
    border: 1px dashed #ddd;
    border-width: 3px 3px;  
    border-radius: 12px;
    transition: border-color 0.1s; 
  }
  .uploadElement >>> .el-upload-dragger:hover {
    border-color: #c6c6c6
  }
  
  .upload-dropzone {
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .divider {
    display: inline-flex;
    align-items: center;
    color: #6D6D6D;
    font-size: 14px;
    margin-bottom: 10px;
  }
  
  .divider::before,
  .divider::after {
    content: " ————";
    flex: 1;
    height: 1px;
    margin-bottom: 15px;
    margin-left: 10px;
    margin-right: 10px;
    color: #e7e7e7;
  }
  
  .file-support {
    font-size: 0.9em;
    color: #6D6D6D;
    text-align: left;
  }
  
  .browse-button {
    width: 119px; 
    height: 30px;
    padding: 5px 10px;
    border: 1px solid #252525; 
    border-radius: 8px; 
    background-color: #FFFFFF; 
    color: #252525; 
    font-size: 14px; 
    font-weight: bold;
    line-height: 1.2; 
    cursor: pointer;
    display: inline-flex; 
    justify-content: center; 
    align-items: center; 
    transition: background-color 0.2s, color 0.2s; 
  }
  
  .browse-button:hover {
    background-color: #e0e0e0; 
    color: #1a1a1a; 
  }
  
  .submit-button {
    padding: 10px 20px;
    background-color: #2C2C2C;
    color: #f5f5f5;
    border: none;
    border-radius: 8px;
    cursor: pointer;
  }
  
  .submit-button:hover {
    background-color: #555;
  }
  
  
  .fixed-left-button {
  position: fixed; /* 固定定位，脱离文档流 */
  bottom: 50px; /* 距页面底部 20px */
  left: 280px; /* 距页面左侧 20px */
  z-index: 1000; /* 确保按钮浮于其他元素上方 */
  }

  .history-button {
    width: 220px;
    height: 40px;
    background-color: #2c2c2c;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    text-align: center;
    font-weight: bold;
    transition: background-color 0.3s ease;
  }

  .history-button:hover {
    background-color: #444;
  }

  .result-section {
    position:flex;
    margin-top: 20px;
  }

  .result-actions {
    margin-top: 20px;
  }

  .result-actions button {
    margin-right: 10px;
    padding: 8px 16px;
    background-color: #2C2C2C;
    color: #f5f5f5;
    border: none;
    border-radius: 8px;
    cursor: pointer;
  }

  .result-actions button:hover {
    background-color: #555;
  }

  .result-content {
    display: flex;
    gap: 20px;
    margin-top: 20px;
  }

  .image-container {
    position: relative;
    flex: 1;
    max-width: 600px;
  }

  .download-overlay {
    position: absolute;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
  }

  .download-overlay button {
    padding: 8px 16px;
    background: rgba(44, 44, 44, 0.8);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .lesion-panel {
    flex: 1;
    max-width: 300px;
  }

  .lesion-buttons {
    display: grid;
    gap: 10px;
  }

  .lesion-buttons button {
    padding: 12px;
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 8px;
    cursor: pointer;
    text-align: left;
  }

  .lesion-buttons button.active {
    background: #2C2C2C;
    color: white;
  }

  .explanation {
    margin-top: 20px;
    padding: 15px;
    background: #f8f8f8;
    border-radius: 8px;
    line-height: 1.5;
  }

  img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  </style>
  