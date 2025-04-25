<template>
    <div class="predict-model">
      
      <BaseStation ref="baseStation" />

      <div class="left-panel">
        <input type="text" placeholder="Search" class="search-input" v-model="searchQuery" />
        
        <div class="model-list">
          <div
            v-for="model in filteredModels"
            :key="model.model_name"
            :class="['model-item', { 'selected-model': model === selectedModel }]"
            @click="selectModel(model)">
            <div style="font-weight: bold; font-size: 20px;">{{ model.model_name }}</div>
          <div class="type">Type: {{ model.model_type }}</div>
          <div class="accuracy">Accuracy: {{ model.model_accuracy }}</div>
          </div>
        </div>
        
      </div>
  
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
            accept=".csv,.zip,.rar"
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
          <p class="file-support">Only support .csv, .zip and .rar files</p>
          <div style="text-align: right;">
            <button class="submit-button" @click="submit" :disabled="isSubmitting">Submit</button>
            <div v-if="loading">
              <LoadComponent ref="loadComponent"/>
            </div>
          </div>

        </div>
        <!-- 预测结果展示 -->
        <div v-if="predictions" class="result-section">
          <p style="margin: 0 auto; height: 30px; width:60%; padding: 20px; background-color: #f0f0f0; color: #333; font-size: 16px; border-radius: 5px; text-align: center; font-weight: bold;">
            Predict Results have been generated.
          </p>
          <div class="result-actions">
            <button @click="downloadFile">Download</button>
            <button @click="clearResults">Clear</button>
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
        allowedExtensions: ['.csv','.zip', '.rar'],
        predictions: null,
        isSubmitting: false,
        loading: false
      };
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
          alert("Request is already in progress.");//防止用户连续提交
          return;
        }

        this.isSubmitting = true;

        //const userId = localStorage.getItem('userID'); 
        // // const modelId = this.selectedModel.model_id; 
        // const stationId = localStorage.getItem('selectedStation');  
        console.log(this.fileList); // 检查上传的文件列表
        const formData = new FormData();
        //formData.append('userid', userId); // 添加 user_id
        // formData.append('model_id', modelId); // 添加 model_id
        // formData.append('station_id', parseInt(stationId,10)); // 添加第一个上传的文件
        formData.append('dataset_file', this.fileList[0].raw); // 添加第一个上传的文件
        console.log(formData); // 检查上传的文件列表
        this.loading = true; // Set loading to true before submission
      
        try {
          const response = await API.post('/api/retinal/upload', formData, {
              headers: { 'Content-Type': 'multipart/form-data' }, // 确保是 multipart/form-data 类型
            });

          //const data = await response.json();
          const data = response.data;

          this.predictions = data.data.predictions; // 保存 predictions 数据
          this.$message.success("Submission successful!");
        } catch (error) {
          console.error("Error submitting data:", error);
          this.$message.error("Submission failed.");
        } finally {
          this.isSubmitting = false;
          this.loading = false; // Set loading to false after submission is complete
        }
      },

      downloadFile() {
        // 预测结果数据
        const predictionsHeader = [
          "Top-1 Prediction",
          "Top-2 Predictions",
          "Top-3 Predictions",
        ];
        const predictionRows = this.predictions.map((prediction) => [
          prediction.top1_pred,
          prediction.top2_pred.join(", "),
          prediction.top3_pred.join(", "),
        ]);

        const csvContent = [
          predictionsHeader.join(","),
          ...predictionRows.map((row) => row.join(",")),
        ].join("\n");

        // 创建 CSV 文件并下载
        const blob = new Blob([csvContent], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "prediction-results.csv";
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

  </style>
  