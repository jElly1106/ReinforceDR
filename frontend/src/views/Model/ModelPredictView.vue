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
          <div style="text-align: right;">
            <button class="submit-button" @click="submit" :disabled="isSubmitting">Submit</button>
            <div v-if="loading">
              <LoadComponent ref="loadComponent"/>
            </div>
          </div>
        </div>
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
    </div>
    <div class="fixed-left-button">
      <button class="history-button" @click="goToHistory">View model prediction history</button>
    </div>
  </template>
  
  <script>
  import 'element-plus/dist/index.css';
  import BaseStation from '../../components/BaseStation.vue';
  import LoadComponent from '../../components/LoadComponent.vue';
  import API from '../../router/axios';

  export default {
    components: {
      BaseStation,
      LoadComponent,
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
        segmentation_id:0,
        processed_image_url:null,
        progress: 0,  // 新增进度状态
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
          // 这里你可以添加任何变化后需要执行的逻辑
        }
      }
    },
    computed: {
      // Filter models based on search query
      // filteredModels() {
      //   return this.models.filter(model => 
      //   model.model_name.toLowerCase().includes(this.searchQuery.toLowerCase())
      //   );
      // }
    },
    methods: {
      async pollSegmentationResult(segmentation_id) {
        const interval = setInterval(async () => {
          try {
            const progressResponse = await API.get(`/api/retinal/segmentation/progress/${segmentation_id}`);
            const progressData = progressResponse.data;
            
            if (progressData.code === 200) {
              this.progress = progressData.data.progress || 0;

              if (progressData.data.status === 'completed') {
                clearInterval(interval);
                const resultResponse = await API.get(`/api/retinal/segmentation/${segmentation_id}`);
                const resultData = resultResponse.data;
                
                if (resultData.code === 200) {
                  this.processed_image_url = resultData.data.combined_url;
                  this.ex_url = resultData.data.ex_url;
                  this.he_url = resultData.data.he_url;
                  this.ma_url = resultData.data.ma_url;
                  this.se_url = resultData.data.se_url;
                  this.currentImageUrl = this.processed_image_url;
                  this.progress = 100;
                  setTimeout(() => this.progress = 0, 2000);
                }
              }

              if (progressData.data.status === 'failed') {
                this.$message.error(`Processing failed: ${progressData.data.error_message}`);
                clearInterval(interval);
                this.progress = 0;
              }
            }
          } catch (error) {
            console.error("Error polling segmentation result:", error);
            clearInterval(interval);
            this.progress = 0;
          }
        }, 2000);
      },

      // 新增病灶显示方法
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

      goToHistory() {
        this.$router.push("history");
       },
      // Fetch models from the backend
      // async fetchModels() {
      //   try {
      //     const selectedStation = localStorage.getItem('selectedStation');
      //     const response = await API.get('/V2I_model/get_model_list/', { 
      //       params: { base_station_id: selectedStation} 
      //     });
    
      //     const data = response.data;
      //     this.models = data.data; // 假设返回的数据中有 `models`
      //     console.log("Models fetched successfully:", this.models);
      //   } catch (error) {
      //     console.error("Error fetching models:", error);
      //   }
      // },
      
      // Select a model
      // selectModel(model) {
      //   this.selectedModel = model;
      // },

      //此函数相当于二次检查，不过一般用不上，因为第一次筛选已经去除了不合要求的文件格式
      handleChange(file, fileList) {
      const fileExtension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
      if (!this.allowedExtensions.includes(fileExtension)) {
        this.$message.error(`Unsupported file format: ${fileExtension}`);
        fileList.splice(fileList.indexOf(file), 1);
        return;
      }
      this.fileList = fileList;
      this.$message.success(`File "${file.name}" added successfully.`);
      },

      // Submit data
      async submit() {
        if (this.fileList.length === 0) {
          alert("Please upload a file.");
          return;
        }

        if (this.isSubmitting) {
          alert("Request is already in progress.");
          return;
        }

        this.isSubmitting = true;
        this.loading = true; // Set loading to true before submission

        const formData = new FormData();
        formData.append('file', this.fileList[0].raw); // 添加第一个上传的文件

        try {
          const response = await API.post('/api/retinal/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }, // 确保是 multipart/form-data 类型
          });

          const data = response.data;
          this.segmentation_id = data.data.segmentation_id;  // 获取 segmentation_id
          this.pollSegmentationResult(this.segmentation_id);  // 调用轮询方法

          this.$message.success("Submission successful!");
        } catch (error) {
          console.error("Error submitting data:", error);
          this.$message.error("Submission failed.");
        } finally {
          this.isSubmitting = false;
          this.loading = false; // Set loading to false after submission is complete
        }
      },

      // 轮询分割结果
      // async pollSegmentationResult(segmentation_id) {
      //   const interval = setInterval(async () => {
      //     try {
      //       const response = await API.get(`/api/retinal/segmentation/${segmentation_id}`);

      //       const data = response.data;
      //       // console.log(data.data);
      //       // console.log(data.data.combined_path);
      //       if (data.code === 200 && data.data.status === 'completed') {
      //         // 处理完成，展示处理后的图像
      //         this.processed_image_url = data.data.combined_url; // 获取处理后的图像 URL
      //         console.log(this.processed_image_url);
      //         clearInterval(interval); // 停止轮询
      //       }
      //     } catch (error) {
      //       console.error("Error polling segmentation result:", error);
      //       clearInterval(interval); // 停止轮询
      //     }
      //   }, 10000); // 每5秒轮询一次
      // },


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
      },

      clearResults() {
        this.predictions = null; // 清空 predictions 数据
      },
    },
    // mounted() {
    //   this.fetchModels();
    // }
  };
  </script>
  
  <style scoped>
  /* 新增进度条样式 */
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
  