<template>
    <div class="station-select">
      <el-select 
        v-model="selectedStationName"
        :placeholder="selectedStationName || 'basestation'"
        :filterable="false" 
        @change="handleStationChange" 
        class="station-dropdown">
    
         <!-- Create Base Station -->
        <el-option
          key="create"
          label="Create Base Station"
          value="create"
          class="custom-option">
          <template v-slot:default>
            <span style="color: #880E4F;font-weight: bold;">Create Base Station<i style="margin-left:5px;font-size:20px">+</i></span>
          </template>
        </el-option>
    
        <!-- Manage Base Stations -->
        <el-option
          key="manage"
          label="Manage Base Stations"
          value="manage"
          class="custom-option">
          <template v-slot:default>
            <span style="color: #880E4F;font-weight: bold">Manage Base Stations<i class="bi-gear-fill" style="margin-left: 5px"></i></span>
          </template>
        </el-option>
    
        <!-- Base Station List -->
        <el-option
          v-for="station in stationList"
          :key="station.base_station_id"
          :label="station.base_station_name"
          :value="station.base_station_id"
          :style="{ color: selectedStation === station.base_station_id ? '#555' : '#6D6D6D' }">
        </el-option>
      </el-select>
    
      <!-- 新建基站弹窗 -->
      <el-dialog
        class="create-station-dialog"
        v-model="isDialogVisible"
        @close="resetDialog"
        width="25%"
        :style="{ textAlign: 'left' }">
        <template v-slot:title>
          <span style="font-size: 20px; font-weight: bold;">Create Base Station</span>
        </template>
    
        <div>
          <el-form :model="newStationForm" style="font-size: 20px; font-weight: 400;">
            <el-row>
              <el-col :span="11">
                <el-form-item>
                  <div>Station Name</div>
                  <el-input class="custom-input" v-model="newStationForm.name" placeholder="Value"></el-input>
                </el-form-item>
              </el-col>
            </el-row>
    
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item>
                  <div>Station Longitude</div>
                  <el-input class="custom-input" v-model="newStationForm.longitude" placeholder="Value"></el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <div>Station Latitude</div>
                  <el-input class="custom-input" v-model="newStationForm.latitude" placeholder="Value"></el-input>
                </el-form-item>
              </el-col>
            </el-row>
    
            <el-row>
              <el-col :span="24">
                <el-form-item>
                  <div>Station Details</div>
                  <el-input
                    class="custom-input"
                    v-model="newStationForm.description"
                    type="textarea"
                    :rows="3"
                    placeholder="Value">
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
    
        <template v-slot:footer>
          <el-button type="primary" @click="submitNewStation">Confirm</el-button>
        </template>
      </el-dialog>
    
      <!-- 编辑基站弹窗 -->
      <el-dialog
      class="manage-station-dialog"
      v-model="isManageDialogVisible"
      width="35%"
      :style="{ textAlign: 'left' }">
      <template v-slot:title>
        <span style="font-size: 20px; font-weight: bold;">Manage Base Station</span>
      </template>
    
      <div style="display: flex;">
    <!-- 左侧基站列表 -->
    <div style="width: 25%; background-color: #f8f8f8; padding: 0px; position: relative;border-top-left-radius: 5px;border-bottom-left-radius: 5px">
      <el-menu :default-active="currentStation" @select="handleStationSelect">
          <el-menu-item
            v-for="station in stationList"
            :key="station.base_station_id"
            :index="station.base_station_id"
            class="station-item"
          >
            <div class="station-item-content">
              <span>{{ station.base_station_name }}</span>
              <el-icon
                class="delete-icon"
                @click.stop="confirmDelete(station.base_station_id)"
              >
                <Delete />
              </el-icon>
            </div>
          </el-menu-item>
      </el-menu>
    </div>

        <!-- 右侧编辑内容 -->
        <div style="width: 75%; padding: 10px;">
          <el-form :model="currentStationForm" style="font-size: 20px; font-weight: 400;">
            <el-row>
              <el-col :span="11">
                <el-form-item>
                  <div>Station Name</div>
                  <el-input class="custom-input" v-model="currentStationForm.name" placeholder="Value"></el-input>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item>
                  <div>Station Longitude</div>
                  <el-input class="custom-input" v-model="currentStationForm.longitude" placeholder="Value"></el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <div>Station Latitude</div>
                  <el-input class="custom-input" v-model="currentStationForm.latitude" placeholder="Value"></el-input>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row>
              <el-col :span="24">
                <el-form-item>
                  <div>Station Details</div>
                  <el-input
                    class="custom-input"
                    v-model="currentStationForm.description"
                    type="textarea"
                    :rows="3"
                    placeholder="Value">
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
      </div>
      <template v-slot:footer>
        <el-button type="primary" @click="submitEditStation">Save</el-button>
      </template>
      </el-dialog>
    </div>
</template>
  
  <script>
  import API from '../router/axios';
  import { ElMessageBox, ElMessage } from "element-plus";

  export default {
    data() {
      return {
        selectedStationName: '',
        isDialogVisible: false, // 控制新建基站弹窗的显示
        isManageDialogVisible: false, // 控制管理基站弹窗的显示
        selectedStation: null,
        currentStation: null, //选择需要编辑的基站的ID
        stationList: [],
        newStationForm: {
          name: '',
          longitude: '',
          latitude: '',
          description: '',
        },
        currentStationForm:{
          name: '',
          longitude: '',
          latitude: '',
          description: '',
        }
      };
    },
    methods: {
      // 基站切换逻辑
      handleStationChange(station) {
        if (station === 'create') {
          this.isDialogVisible = true;
        } else if (station === 'manage') {
          this.isManageDialogVisible = true;
        } else {
          this.selectedStation = station;
          const basestation = this.stationList.find(
          (s) => s.base_station_id === this.selectedStation
          );
          this.selectedStationName = basestation.base_station_name;
          localStorage.setItem('selectedStation', station);
          localStorage.setItem('selectedStationName', basestation.base_station_name);
        }
      },
  
      // 获取基站数据
     async fetchStations() {
       try {
         const userId = localStorage.getItem('userID');  // 获取用户ID
         if (!userId) {
            throw new Error("User ID is required.");
         }
         const response = await API.get('/data/base_stations/my/', { params: { user_id: userId } });
         
         this.stationList = response.data.data;  
         if (this.stationList.length > 0) {
            this.currentStation = this.stationList[0].base_station_id;  
         }

         // 读取选择的基站（如果有保存）
        const savedStation = localStorage.getItem('selectedStation');
        if (savedStation) {
          this.selectedStation = savedStation;
          this.selectedStationName = localStorage.getItem('selectedStationName');
        }
        
      } catch (error) {
         console.error("Error fetching stations:", error);
      }
    },

      // 提交新建基站
    async submitNewStation() {
      // 检查基站名称是否为空
      if (!this.newStationForm.name.trim()) {
        this.$message.error("Base station name cannot be empty!");
        return;
      }
      
      // 检查基站名称是否已存在
      if (this.stationList.some(station => station.name === this.newStationForm.name)) {
        this.$message.error("Station name already exists!");
        return; 
      }

      // 检查基站名称长度限制
      if (this.newStationForm.name.length < 2 || this.newStationForm.name.length > 50) {
        this.$message.error("Base station name must be between 2 and 50 characters!");
        return;
      }

      // 检查基站名称是否只包含允许的字符（字母、数字、空格、下划线）
      if (!/^[a-zA-Z0-9\s_]+$/.test(this.newStationForm.name)) {
        this.$message.error("Base station name can only contain letters, numbers, spaces, and underscores!");
        return;
      }

      // 检查经纬度是否为空
      if (!this.newStationForm.longitude || !this.newStationForm.latitude) {
        this.$message.error("Please fill in the longitude and latitude completely!");
        return;
      }

      // 检查经纬度是否为数字
      if (isNaN(this.newStationForm.longitude) || isNaN(this.newStationForm.latitude)) {
        this.$message.error("Longitude and latitude must be numbers!");
        return;
      }

      // 检查纬度是否在 -90 到 90 度之间
      if (this.newStationForm.latitude < -90 || this.newStationForm.latitude > 90) {
        this.$message.error("Latitude must be between -90 and 90 degrees!");
        return;
      }

      // 检查经度是否在 -180 到 180 度之间
      if (this.newStationForm.longitude < -180 || this.newStationForm.longitude > 180) {
        this.$message.error("Longitude must be between -180 and 180 degrees!");
        return;
      }

      try {
        const userId = localStorage.getItem('userID');
        if (!userId) {
          this.$message.error("User is not logged in or failed to retrieve user ID!");
          return;
        }

        const payload = {
          latitude: this.newStationForm.latitude,
          longitude: this.newStationForm.longitude,
          description: this.newStationForm.description,
          user_id: userId,
          base_station_name: this.newStationForm.name,
        };

        // 使用 Axios 发送 POST 请求
        const response = await API.post('data/base_stations/create/', payload);

        // 成功创建基站
        const newStation = response.data;

        this.stationList.push(newStation); // 更新基站列表
        this.$message.success("Base station created successfully!");
        this.isDialogVisible = false; // 关闭弹窗
        this.resetDialog(); // 重置表单
      } catch (error) {
      // 处理网络错误或系统错误
      if (error.response) {
        const errorMessage = error.response.data.message;
        console.error("Failed to create base station:", error.response.data);
        this.$message.error(errorMessage || "Failed to create base station!");
      } else if (error.request) {
          // 请求发送成功但未收到响应
          console.error("No response received:", error.request);
          this.$message.error("No response from server. Please try again later!");
        } else {
            // 请求未发送成功
            console.error("Request setup error:", error.message);
            this.$message.error("Network error occurred while creating base station. Please check your connection!");
        }
      }
    },
    // 关闭弹窗，重置表单
    resetDialog() {
      this.newStationForm = {
        name: '',
        longitude: '',
        latitude: '',
        description: '',
      };
      this.isDialogVisible = false;
    },

    // 选择需要编辑的基站
    handleStationSelect(stationId) {
      const editedStation = this.stationList.find(station => station.base_station_id === Number(stationId));
      if (editedStation) {
        this.currentStationForm = {
          name: editedStation.base_station_name,
          longitude: editedStation.longitude,
          latitude: editedStation.latitude,
          description: editedStation.description,
        };
      }
      this.currentStation = stationId; // 更新当前选中基站
    },

    confirmDelete(stationId) {
    ElMessageBox.confirm(
      "Are you sure you want to delete this station?",
      "Delete Confirmation",
      {
        confirmButtonText: "Confirm",
        cancelButtonText: "Cancel",
        customClass: "custom-message-box", 
      }
    )
      .then(() => {
        this.deleteStation(stationId);
      })
      .catch(() => {
        ElMessage({
          type: "info",
          message: "Deletion canceled.",
        });
      });
    },
    
    async deleteStation(stationId) {
      try {
        // 检查是否提供了 stationId
        if (!stationId) {
            this.$message.error("Base station ID is required!");
            return;
        }

        // 调用后端 DELETE 接口
        await API.delete('/data/base_stations/delete/', {
            params: {
                base_station_id: stationId, // 基站ID作为查询参数传递
            },
        });

        // 检查响应状态
        console.log("删除的基站 ID:", stationId);
        const destation = parseInt(localStorage.getItem('selectedStation'), 10);
        if(destation === stationId) {
          localStorage.removeItem('selectedStation');
          localStorage.removeItem('selectedStationName');
          console.log(localStorage.getItem('selectedStation'));
        }
        // 更新 stationList，移除已删除的基站
        this.stationList = this.stationList.filter(
            (station) => station.base_station_id !== stationId
        );
      
        this.$message.success("Base station deleted successfully!");
      } catch (error) {
        this.$message.error("Failed to delete base station!");
        console.error("Error during deleteStation:", error);
      }
    },
    async submitEditStation() {
      try {
        const userId = localStorage.getItem('userID'); 
        if (!userId) {
            this.$message.error("User is not logged in or failed to retrieve user ID!");
            return;
        }

        const baseStationId = this.currentStation; // 当前基站ID
        if (!baseStationId) {
            this.$message.error("Base station ID is missing!");
            return;
        }

        // 检查基站名称是否为空
        if (!this.currentStationForm.name.trim()) {
          this.$message.error("Base station name cannot be empty!");
          return;
        }
        
        // 检查基站名称是否已存在
        if (this.stationList.some(station => station.name === this.currentStationForm.name)) {
          this.$message.error("Station name already exists!");
          return; 
        }
  
        // 检查基站名称长度限制
        if (this.currentStationForm.name.length < 2 || this.currentStationForm.name.length > 50) {
          this.$message.error("Base station name must be between 2 and 50 characters!");
          return;
        }
  
        // 检查基站名称是否只包含允许的字符（字母、数字、空格、下划线）
        if (!/^[a-zA-Z0-9\s_]+$/.test(this.currentStationForm.name)) {
          this.$message.error("Base station name can only contain letters, numbers, spaces, and underscores!");
          return;
        }
  
        // 检查经纬度是否为空
        if (!this.currentStationForm.longitude || !this.currentStationForm.latitude) {
          this.$message.error("Please fill in the longitude and latitude completely!");
          return;
        }
  
        // 检查经纬度是否为数字
        if (isNaN(this.currentStationForm.longitude) || isNaN(this.currentStationForm.latitude)) {
          this.$message.error("Longitude and latitude must be numbers!");
          return;
        }
  
        // 检查纬度是否在 -90 到 90 度之间
        if (this.currentStationForm.latitude < -90 || this.currentStationForm.latitude > 90) {
          this.$message.error("Latitude must be between -90 and 90 degrees!");
          return;
        }
  
        // 检查经度是否在 -180 到 180 度之间
        if (this.currentStationForm.longitude < -180 || this.currentStationForm.longitude > 180) {
          this.$message.error("Longitude must be between -180 and 180 degrees!");
          return;
        }
  
        const { name, longitude, latitude, description } = this.currentStationForm;

        const payload = {
            base_station_id: baseStationId,
            base_station_name: name,
            longitude,
            latitude,
            description,
            user_id: userId,
        };

        // 发送 PUT 请求
        const response = await API.put('/data/base_stations/update/', payload);

        this.$message.success("Base station updated successfully!");
        const updatedStation = response.data;

        // 更新本地的基站列表
        const index = this.stationList.findIndex(station => station.base_station_id === baseStationId);
        if (index !== -1) {
          this.stationList[index] = updatedStation;
        }

        // 关闭对话框并重置表单
        this.isManageDialogVisible = false;
        this.currentStationForm = {
            name: '',
            longitude: '',
            latitude: '',
            description: '',
        };
      } catch (error) {
          this.$message.error("Failed to update base station!");
          console.error("Error during submitEditStation:", error);
      }
    }
  },
  mounted() {
    this.fetchStations();
  }
  };
  </script>
  
  <style scoped>
.station-select {
  position:absolute;
  top: 12px;
  right: 280px;
  display: flex;
  align-items: center;
}

.station-dropdown {
  width: 160px;
}


/* .station-dropdown >>> .el-select__placeholder {
  color:#555;
  font-size: 16px;
}  */

/* .station-dropdown >>> .el-select__wrapper {
  box-shadow: 0 0 0 1px #ffffff inset;
} */

/* .station-dropdown >>> .el-select__selection {
  font-size: 16px;
  font-weight:600;
} */

:deep(.el-select__placeholder)  {
  color:#555;
  font-size: 16px;
}

:deep(.el-select__wrapper) {
  box-shadow: 0 0 0 1px #ffffff inset;
}

:deep(.el-select__wrapper.is-hovering:not(.is-focused)) {
  box-shadow: 0 0 0 1px #ffffff inset;
}

:deep(.el-select__selection) {
  font-size: 16px;
  font-weight:600;
} 

.custom-option {
  font-size: 14px;
  font-weight: 500;
}

.dialog-footer {
  text-align: right;
}

.el-input{
  --el-input-border-radius: 8px;
  --el-input-focus-border-color: black;
  --el-input-focus-shadow-color: rgba(0, 0, 0, 0.1);
  transition: border-color 0.3s, box-shadow 0.3s; /* 添加过渡效果 */
}
.el-textarea{
  --el-input-border-radius: 8px;
  --el-input-focus-border-color: black;
  --el-input-focus-shadow-color: rgba(0, 0, 0, 0.1);
  transition: border-color 0.3s, box-shadow 0.3s; /* 添加过渡效果 */
}

.el-button--primary {
    --el-button-border-color: #630A45;
    --el-button-bg-color: #630A45;
    --el-button-hover-bg-color:#7b3a66;
    --el-button-hover-border-color: #7b3a66;
    --el-button-active-bg-color: #7b3a66;
    --el-button-active-border-color: #7b3a66;
}

.el-button{
  width:79px;
  height: 32px;
   border-radius: 8px;
}

::v-deep .el-icon:hover {
  --el-icon-hover-color: black; 
  color: var(--el-icon-hover-color); 
}

::v-deep .el-dialog__headerbtn:hover .el-icon {
  color: black !important; 
}

.station-item-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.delete-icon {
  position: absolute;
  color: #252525;
  cursor: pointer;
  right: 5%;
  font-weight: bold;
}
::v-deep .el-menu {
  background-color: #f8f8f8;
  font-weight: bold;
}

::v-deep .el-menu-item.is-active {
  background-color: #F2F2F2;
  color:#252525
}

::v-deep .el-menu-item:hover {
  background-color: #F2F2F2;
}

</style>
  