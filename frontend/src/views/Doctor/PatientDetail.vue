<template>
  <div class="history-page">
    <!-- 左侧栏：患者信息 -->
    <aside class="sidebar" v-if="patient">
      <h3>Patient Info</h3>
      <p><strong>Name:</strong> {{ patient.name }}</p>
      <p><strong>Gender:</strong> {{ patient.gender }}</p>
      <p><strong>Age:</strong> {{ patient.age }}</p>
      <p><strong>Phone:</strong> {{ patient.phone }}</p>
    </aside>

    <!-- 右侧内容区域 -->
    <main class="main-content">
      <h2>History of Retinal Image Segmentation</h2>

      <!-- 上传区域 -->
      <div class="upload-area">
        <h3>Upload New Image for Prediction</h3>
        <div class="upload-container">
          <input 
            type="file" 
            ref="fileInput" 
            @change="handleFileSelect" 
            accept=".png,.jpg,.jpeg,.bmp,.tif,.tiff" 
            style="display: none"
          >
          <button class="select-file-btn" @click="triggerFileSelect">
            <el-icon><upload-filled /></el-icon> Select File
          </button>
          <span v-if="file" class="file-name">{{ file.name }}</span>
          <button 
            class="predict-btn" 
            @click="submitUpload" 
            :disabled="!file || isUploading"
          >
            {{ isUploading ? 'Processing...' : 'Predict' }}
          </button>
        </div>
        <div v-if="isUploading" class="progress-display">
          <p>Processing: {{ progress }}%</p>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progress + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- 每页项数选择 -->
      <div class="page-size-selector">
        <label for="page-size">Items per page:</label>
        <select v-model="itemsPerPage" @change="fetchHistory">
          <option value="2">2</option>
          <option value="3">3</option>
          <option value="5">5</option>
          <option value="10">10</option>
        </select>
      </div>

      <!-- 图像历史记录 -->
      <div class="history-list">
        <div v-for="(item, index) in historyItems" :key="index" class="history-item">
          <div class="image-container">
            <img :src="item.image_url" alt="Image" class="history-image" />
          </div>
          <div class="history-info">
            <h3>{{ item.image_name }}</h3>
            <p class="description">{{ item.description }}</p>
            <p class="status">Segmentation Status: {{ item.segmentation ? item.segmentation.status : 'Pending' }}</p>
            <button class="view-btn" @click="viewSegmentationResult(item.id)">
              View Segmentation Result
            </button>
          </div>
        </div>
      </div>

      <!-- 分页导航 -->
      <div class="pagination">
        <button @click="changePage(page - 1)" :disabled="page <= 1">Previous</button>
        <span>Page {{ page }} of {{ totalPages }}</span>
        <button @click="changePage(page + 1)" :disabled="page >= totalPages">Next</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { UploadFilled } from '@element-plus/icons-vue';
import API from '../../router/axios';
import { defineProps } from 'vue';

const router = useRouter();
const fileInput = ref(null);
const file = ref(null);
const isUploading = ref(false);
const progress = ref(0);

const historyItems = ref([]);
const patient = ref(null);
const page = ref(1);
const totalPages = ref(1);
const itemsPerPage = ref(3);

const triggerFileSelect = () => fileInput.value.click();

const handleFileSelect = (e) => {
  const selectedFile = e.target.files[0];
  if (selectedFile) {
    const ext = selectedFile.name.slice(selectedFile.name.lastIndexOf('.')).toLowerCase();
    const allowed = ['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'];
    if (!allowed.includes(ext)) {
      alert(`Unsupported file format: ${ext}`);
      return;
    }
    file.value = selectedFile;
  }
};

const props = defineProps({ id: String });

const submitUpload = async () => {
  if (!file.value) return alert("Please select a file.");

  let patientId = props.id;
  if (!patientId) {
    patientId = prompt("Please enter patient ID:");
    if (!patientId) return alert("Patient ID is required.");
  }

  if (isUploading.value) return;

  isUploading.value = true;
  progress.value = 0;

  const formData = new FormData();
  formData.append('patient_id', patientId);
  formData.append('file', file.value);

  try {
      const res = await API.post('/api/retinal/upload', formData, {
            headers: {
            'Content-Type': 'multipart/form-data' // 明确指定为 multipart/form-data
            }
        });
    const data = res.data;

    if (data.code === 200) {
      const segmentationId = data.data.segmentation_id;
      progress.value = 30;

      const poll = async () => {
        try {
          const pollRes = await API.get(`/api/retinal/segmentation/progress/${segmentationId}`);
          const pollData = pollRes.data;
          if (pollData.code === 200) {
            progress.value = 30 + Math.floor(pollData.data.progress * 0.7);
            if (pollData.data.status === 'completed') {
              viewSegmentationResult(segmentationId);
              isUploading.value = false;
              file.value = null;
              progress.value = 0;
              fetchHistory();
            } else if (pollData.data.status === 'failed') {
              isUploading.value = false;
              alert(`Processing failed: ${pollData.data.error_message}`);
            } else {
              setTimeout(poll, 2000);
            }
          }
        } catch (err) {
          console.error("Polling error:", err);
          isUploading.value = false;
        }
      };

      setTimeout(poll, 2000);
    } else {
      throw new Error(data.message || 'Upload failed');
    }
  } catch (err) {
    console.error("Upload error:", err);
    alert("Upload failed: " + err.message);
    isUploading.value = false;
    progress.value = 0;
  }
};

const fetchHistory = async () => {
  try {
    const res = await API.get(`/api/patient/patient-detail/${props.id}`);
    const data = res.data;

    if (data.code === 200) {
      patient.value = {
        name: data.data.name,
        age: data.data.age,
        gender: data.data.gender,
        phone: data.data.phone
      };
      historyItems.value = data.data.images || [];
      totalPages.value = Math.ceil(data.data.image_count / itemsPerPage.value);
    }
  } catch (err) {
    console.error("Fetch history error:", err);
  }
};

const changePage = (newPage) => {
  if (newPage < 1 || newPage > totalPages.value) return;
  page.value = newPage;
  fetchHistory();
};

const viewSegmentationResult = (id) => {
  if (id) {
    router.push({ name: 'segmentationResult', params: { id } });
  } else {
    alert('No segmentation result available yet');
  }
};

onMounted(fetchHistory);
</script>

<style scoped>
.history-page {
  display: flex;
  gap: 2rem;
  max-width: 5000px;
  margin: 2rem auto;
  padding: 1rem;
}

.sidebar {
  flex: 0 0 250px;
  background-color: #f0f2f5;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  color: #333;
}

.sidebar h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.upload-area,
.history-list,
.pagination {
  margin-bottom: 2rem;
}

.history h2,
.main-content h2 {
  font-size: 2rem;
  text-align: center;
  color: #2c3e50;
}

.upload-area {
  background-color: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.upload-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.select-file-btn,
.predict-btn {
  padding: 0.7rem 1.2rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.select-file-btn {
  background-color: #7f34db;
  color: white;
}

.select-file-btn:hover {
  background-color: #6a2bb8;
}

.predict-btn {
  background-color: #2c2c2c;
  color: white;
}

.predict-btn:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.progress-display {
  margin-top: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
  padding: 0.8rem;
}

.progress-bar {
  height: 8px;
  background: #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #7f34db;
  transition: width 0.3s ease;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.history-item {
  display: flex;
  background-color: #ffffff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  gap: 1.5rem;
}

.image-container img {
  max-width: 300px;
  border-radius: 6px;
}

.history-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.view-btn {
  margin-top: 1rem;
  background-color: #7f34db;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.6rem 1.2rem;
  cursor: pointer;
}

.view-btn:hover {
  background-color: #5d24a4;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.page-size-selector {
  text-align: center;
  margin-bottom: 1rem;
}
</style>
