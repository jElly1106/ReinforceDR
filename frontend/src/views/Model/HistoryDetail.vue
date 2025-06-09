<template>
  <div class="predict-model">
    <!-- 回退按钮 -->
    <div class="top-bar">
      <button class="back-button" @click="$router.go(-1)">← Back</button>
    </div>

    <!-- 预测结果展示 -->
    <div class="result-section" v-show="processed_image_url">
      <div class="result-content">
        <!-- 图像区域 -->
        <div class="image-container">
          <img :src="currentImageUrl" alt="Processed Image" />
          <div class="download-overlay">
            <button @click="downloadFile">Download Image</button>
          </div>
        </div>

        <!-- 病变按钮与说明 -->
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
</template>

<script>
import 'element-plus/dist/index.css';
import API from '../../router/axios';

export default {
  props: ['id'],
  data() {
    return {
      processed_image_url: null,
      currentImageUrl: null,
      currentLesion: 'combined',
      currentExplanation: 'Combined lesion detection results',
      ex_url: null,
      he_url: null,
      ma_url: null,
      se_url: null,
      lesions: [
        { type: 'combined', label: 'Combined', explanation: 'A comprehensive detection of all types of retinal lesions (hard exudates, hemorrhages, microaneurysms, soft exudates) for evaluating the severity of diabetic retinopathy or other retinal diseases.' },
        { type: 'ex', label: 'EX', explanation: 'Yellow or white deposits on the retina, mainly composed of lipoproteins and lipids, usually found in areas of vascular leakage. Common in diabetic retinopathy and hypertension, and can lead to macular edema and vision impairment.' },
        { type: 'he', label: 'HE', explanation: 'Blood leakage from retinal vessels, appearing as deep red, dot-shaped, or flame-like lesions. Common in diabetic retinopathy, retinal vein occlusion, and hypertension, and can cause sudden vision loss in severe cases.' },
        { type: 'ma', label: 'MA', explanation: 'Small red dots (15-60 microns) in the retinal capillary walls, often seen in diabetic retinopathy. They are early signs of the disease and may leak, causing retinal edema.' },
        { type: 'se', label: 'SE', explanation: 'White, fluffy spots caused by ischemic infarction of the retinal nerve fiber layer. They are common in diabetes, hypertension, or retinal artery occlusion, indicating local microcirculation issues and potential vision loss.' }
      ]
    };
  },
  created() {
    this.fetchSegmentationResult();
  },
  methods: {
    async fetchSegmentationResult() {
      if (!this.id) {
        console.error('No segmentation ID provided');
        return;
      }
      try {
        const response = await API.get(`/api/retinal/segmentation/${this.id}`);
        const resultData = response.data;
        if (resultData.code === 200) {
          const result = resultData.data;
          this.processed_image_url = result.combined_url;
          this.ex_url = result.ex_url;
          this.he_url = result.he_url;
          this.ma_url = result.ma_url;
          this.se_url = result.se_url;
          this.currentImageUrl = this.processed_image_url;
        } else {
          console.error('Error:', resultData.message);
        }
      } catch (error) {
        console.error("Error fetching result:", error);
      }
    },
    showLesion(type) {
      this.currentLesion = type;
      switch (type) {
        case 'combined': this.currentImageUrl = this.processed_image_url; break;
        case 'ex': this.currentImageUrl = this.ex_url; break;
        case 'he': this.currentImageUrl = this.he_url; break;
        case 'ma': this.currentImageUrl = this.ma_url; break;
        case 'se': this.currentImageUrl = this.se_url; break;
      }
      this.currentExplanation = this.lesions.find(l => l.type === type).explanation;
    },
    downloadFile() {
      if (!this.currentImageUrl) {
        this.$message.error("No image to download");
        return;
      }
      const link = document.createElement('a');
      link.href = this.currentImageUrl;
      link.download = `lesion_${this.currentLesion}_${Date.now()}.jpg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }
};
</script>

<style scoped>
.predict-model {
  max-width: 1200px;
  margin: 30px auto;
  padding: 20px;
  border-radius: 16px;
  background-color: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

.top-bar {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 20px;
}

.back-button {
  background-color: #2C2C2C;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.back-button:hover {
  background-color: #444;
}

.result-section {
  margin-top: 10px;
}

.result-content {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  justify-content: center;
}

.image-container {
  position: relative;
  max-width: 600px;
  width: 100%;
}

img {
  width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.download-overlay {
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
}

.download-overlay button {
  background-color: #2C2C2C;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
}

.download-overlay button:hover {
  background-color: #444;
}

.lesion-panel {
  max-width: 300px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.lesion-buttons {
  display: grid;
  gap: 10px;
}

.lesion-buttons button {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  text-align: left;
  font-weight: 500;
  transition: all 0.3s ease;
}

.lesion-buttons button:hover {
  background-color: #eee;
}

.lesion-buttons button.active {
  background-color: #2C2C2C;
  color: white;
}

.explanation {
  background-color: #fafafa;
  padding: 15px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}
</style>
