<template>
  <div class="table">
    <h2>Manage Model</h2>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Type</th>
          <th>Time</th>
          <th>Accuracy</th>
          <th>Operation</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="model in models" :key="model.model_id">
          <td>
            <input 
              v-if="model.isEditing" 
              v-model="model.newName" 
              @keyup.enter="saveModelName(model)" 
              @blur="model.isEditing = false"
            />
            <span v-else>
              {{ model.name }}
              <button class="edit-btn" @click="enableEditing(model)">
                <i class="bi bi-pencil"></i>
              </button>
            </span>
          </td>
          <td>{{ model.type }}</td>
          <td>{{ model.time }}</td>
          <td>{{ model.accuracy }}</td>
          <td>
            <button class="operation" @click="deleteModel(model)">Delete</button>
            <button class="operation" @click="downloadModel(model)">Download</button>
            <button class="operation" @click="viewReport(model.model_id)">View Report</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import 'bootstrap-icons/font/bootstrap-icons.css';
import API from '../router/axios';

export default {
  name: 'ModelTable', 
  data() {
    return {
      models: []  
    };
  },
  methods: {
    async fetchModels(baseStationId) {
      try {
        
        const response = await API.get('/V2I_model/get_models_by_basestation/', { params: { base_station_id: baseStationId } });
        if (response.status === 200) {
          const models = response.data.data;
          if (models && models.length > 0) {
            this.models = models.map(model => ({
              model_id: model.model_id,
              name: model.model_name,
              type: model.model_type,
              accuracy: `${(model.model_accuracy * 100).toFixed(2)}%`, 
              time: this.formatTime(model.upload_time),
            }));
          } else {
            this.models = [];
            this.$message.info("No model available for this base station");
          }
        } else {
          this.$message.error("Failed to load model list");
        }
      } catch (error) {
        console.error("Error loading model list:", error);
        this.$message.error("Failed to load model list");
      }
    },
    formatTime(isoString) {
      const date = new Date(isoString);
      
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0'); // 月份从0开始，所以要加1
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');
      
      // 使用 '-' 作为日期和时间的分隔符
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    },
    enableEditing(model) {
      model.isEditing = true;
      model.newName = model.name;
    },
    async saveModelName(model) {
      if (model.newName && model.newName !== model.name) {
        try {
          const userId = localStorage.getItem('userID'); 
          // const userId = 1; 
          console.log(model.model_id);
          const response = await API.put('/V2I_model/modify_model_detail/', {
            model_id: model.model_id,
            user_id: userId,
            new_model_name: model.newName,
          });
          if (response.status === 200) {
            model.name = model.newName;
            this.$message.success("Model name updated successfully");
          } else {
            this.$message.error("Failed to update model name");
          }
        } catch (error) {
          console.error("Error updating model name:", error);
          this.$message.error("Failed to update model name");
        }
      }
      model.isEditing = false;
    },
    async deleteModel(model) {
      const userId = localStorage.getItem('userID'); 
      // const userId = 1; // 或从 localStorage 获取
      try {
        const response = await API.delete(`/V2I_model/delete_model/`, {
          params: { user_id: userId, model_id: model.model_id }
        });
        if (response.status === 200) {
          this.models = this.models.filter(m => m.model_id !== model.model_id);
          this.$message.success("Model deleted successfully");
        } else {
          this.$message.error("Failed to delete model");
        }
      } catch (error) {
        console.error("Error deleting model:", error);
        this.$message.error("Failed to delete model");
      }
    },
    async downloadModel(model) {
      // const userId = 1; // 从用户登录状态或其他来源获取用户 ID
      const userId = localStorage.getItem('userID'); 
      try {
        const response = await API.get('/V2I_model/get_model_zip/', {
          params: {
            user_id: userId,
            model_id: model.model_id
          },
          responseType: 'arraybuffer'
        });

        const blob = new Blob([response.data], { type: 'application/zip' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${model.name}.zip`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link); // 移除链接
        window.URL.revokeObjectURL(url);

        this.$message.success("Model downloaded successfully");
      } catch (error) {
        console.error("Error downloading model:", error);
        this.$message.error("Failed to download model");
      }
    },
    viewReport(model_id) {
      this.$router.push({ path: 'trainreport', query: { model_id } });
    }
  }
};
</script>


<style scoped>
h2 {
  font-weight: bold;
  width: 80%;
  margin: 5% 10% 2% 10%;
  text-align: left; 
}

table {
  width: 80%;
  margin: 0 10%;
}

th, td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.operation {
  margin-right: 5px;
  background-color: black; 
  color: white;
  border: none; 
  border-radius: 5px; 
  cursor: pointer;
  font-size: 12px;
  padding: 5px 10px; 
  transition: background-color 0.3s ease;
}

.operation:hover {
  background-color: #2f3640;
}

.edit-btn {
  background: none;    
  border: none;       
  cursor: pointer;   
  font-size: 12px;      
  padding: 0;          
  margin-left: 5px;
}

.edit-btn i {
  font-size: 12px; 
}

.bi-question-circle {
  margin-left: 2px;
  font-size: 12px;
  color: #555;
  cursor: pointer;
  transition: color 0.3s;
}

.bi-question-circle:hover {
  color: #000;
}

td:nth-child(3) {
  font-size: 14px; 
}
</style>
