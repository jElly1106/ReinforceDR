<template>
  <div class="predict-model">
    <div class="left-panel">
      <BaseStation ref="baseStation" />
    </div>

    <div class="right-panel">
      <!-- 预测结果展示 -->
      <div class="result-section" v-show="processed_image_url">
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
  </div>
</template>

<script>
import 'element-plus/dist/index.css';
import BaseStation from '../../components/BaseStation.vue';
import API from '../../router/axios';

export default {
  props: ['id'], // 自动接收路由参数
  components: {
    BaseStation,
  },
  data() {
    return {
      models: [],
      selectedModel: null,
      searchQuery: "",
      fileList: [], 
      allowedExtensions: ['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'],
      predictions: null,
      isSubmitting: false,
      loading: false,
      segmentation_id: 0,
      processed_image_url: null,
      progress: 0,
      ex_url: null,
      he_url: null,
      ma_url: null,
      se_url: null,
      currentImageUrl: null,
      currentLesion: 'combined',
      currentExplanation: 'Combined lesion detection results',
      lesions: [
        { 
          type: 'combined', 
          label: 'Combined', 
          explanation: '综合病变检测结果，包含所有类型的眼底病变（硬性渗出、出血、微动脉瘤、软性渗出等），用于整体评估糖尿病视网膜病变或其他视网膜疾病的严重程度。' 
        },
        { 
          type: 'ex', 
          label: 'EX', 
          explanation: '硬性渗出（Hard Exudates, EX）是视网膜上的黄色或白色沉积物，主要由脂蛋白和脂质组成，通常出现在血管渗漏区域。它们呈边界清晰的斑点状或斑块状，常见于糖尿病视网膜病变（Diabetic Retinopathy, DR）或高血压视网膜病变。长期积累可能导致黄斑水肿，影响中心视力。' 
        },
        { 
          type: 'he', 
          label: 'HE', 
          explanation: '出血（Hemorrhages, HE）是指视网膜血管破裂导致的血液外渗，表现为深红色点状、片状或火焰状病灶。根据出血位置可分为视网膜内出血（点状或斑块状）和视网膜前出血（大片状）。常见于糖尿病视网膜病变、视网膜静脉阻塞或高血压等疾病，严重时可能导致玻璃体积血，造成视力骤降。' 
        },
        { 
          type: 'ma', 
          label: 'MA', 
          explanation: '微动脉瘤（Microaneurysms, MA）是糖尿病视网膜病变最早的临床征象，表现为视网膜毛细血管壁局部膨出形成的红色小点（直径约15-60微米）。通常分布在黄斑周围，可通过荧光血管造影（FFA）清晰显示。微动脉瘤可能渗漏导致视网膜水肿，是疾病进展的重要标志。' 
        },
        { 
          type: 'se', 
          label: 'SE', 
          explanation: '软性渗出（Soft Exudates, SE），又称棉絮斑（Cotton Wool Spots），是视网膜神经纤维层缺血性梗死导致的白色絮状病灶，边界模糊。其本质是轴浆运输中断导致的细胞内物质堆积。常见于糖尿病、高血压或视网膜动脉阻塞等疾病，提示局部微循环障碍，可能伴随视力下降。' 
        }
      ]
    };
  },
  watch: {
    processed_image_url(newVal, oldVal) {
      if (newVal) {
        console.log('processed_image_url has changed:', newVal);
        console.log('processed_image_url has changed:', oldVal);
      }
    }
  },
  created() {
    this.fetchSegmentationResult();
  },
  methods: {
    async fetchSegmentationResult() {
      try {
        if (!this.id) {
          console.error('No segmentation ID provided');
          return;
        }
        
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
          console.error('Error fetching segmentation result:', resultData.message);
        }
      } catch (error) {
        console.error("Error fetching segmentation result:", error);
      }
    },

    showLesion(type) {
      this.currentLesion = type;
      switch(type) {
        case 'combined':
          this.currentImageUrl = this.processed_image_url;
          break;
        case 'ex':
          this.currentImageUrl = this.ex_url;
          break;
        case 'he':
          this.currentImageUrl = this.he_url;
          break;
        case 'ma':
          this.currentImageUrl = this.ma_url;
          break;
        case 'se':
          this.currentImageUrl = this.se_url;
          break;
      }
      this.currentExplanation = this.lesions.find(l => l.type === type).explanation;
    },

    downloadFile() {
      if (!this.currentImageUrl) {
        this.$message.error("No image available to download");
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
  display: flex;
  height: 90%;
  font-family: Arial, sans-serif;
  border: 1px solid #E5E5E5;
  margin-left: 35px;
  margin-right: 35px;
  margin-top: 10px;
  margin-bottom: 15px;
  border-radius: 20px;
}

.right-panel {
  width: 90%; 
  padding: 20px;
  margin: 0 auto;
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
  max-width: 1200px;
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