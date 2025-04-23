<template>
  <div class="admin-container">
    <div class="header">
      <TopBar />
    </div>
    <div class="table-container">
      <h1>Dataset Review</h1>
      <div class="table">
        <table>
          <thead>
            <tr>
              <th></th>
              <th>Base Station Name</th>
              <th>
                Uploaded Time
                <i class="bi bi-question-circle"
                  title="This column shows the time of the dataset uploaded by user."></i>
              </th>
              <th>
                Dataset Status
                <i class="bi bi-question-circle"
                  title="This column indicates the current state of the dataset (e.g., Pending, Approved,Rejected)."></i>
              </th>
              <th>
                Model Status
                <i class="bi bi-question-circle"
                  title="This column displays the current state of the model (e.g.,Uploaded, Unuploaded)."></i>
              </th>
              <th>Operation</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="model in models" :key="model.dataset_id">
              <td></td>
              <td>{{ model.base_station_name }}</td>
              <td>{{ model.upload_time }}</td>
              <td>
                <img :src="getStateIcon(model.dataset_status)" alt="State Icon" class="state-icon" />
              </td>
              <td class="icon">{{ model.model_status }}</td>
              <td>
                <button class="operation" @click="get_oss_dataset(model)">Download</button>
                <button class="operation" @click="reviewDialogVisible=true;reviewId=model.dataset_id">Review</button>
                <button class="operation" :disabled="!model.model_can_train" @click="model_train(model)">Train</button>
              </td>

              <el-dialog v-model="reviewDialogVisible" title="Review the Dataset" width="500" center>
                <el-select v-model="value" placeholder="Select" style="width: 240px ;margin:10px">
                  <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value"
                    :disabled="item.disabled" />
                </el-select>
                <el-input v-if="value == 'rejected'" v-model="rejectedReason" placeholder="Rejection Reason" style="width: 240px ;margin:10px" />
                <el-button class="operation" @click="reviewDataset()">Submit</el-button>
              </el-dialog>
              <!-- <el-dialog v-model="uploadDialogVisible" width="700" center>
                <div class="upload-section">
                  <h2>Upload the Model File</h2>
                  <el-upload ref="uploadDom" action="" v-model:file-list="fileList" :auto-upload="false" multiple drag
                    accept=".zip,.rar" :on-change="handleChange" class="uploadElement">
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <p style="font-size: 16px; margin-top: -5px;color:black">Drag the model file to start uploading</p>
                    <div class="upload-dropzone">
                      <span class="divider">OR</span>
                      <button class="browse-button">Browse files</button>
                    </div>
                  </el-upload>
                  <div class="submit-section">
                    <button class="submit-button" @click="submit">Submit</button>
                  </div>
                </div>
              </el-dialog> -->
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

</template>

<script setup>
import TopBar from '@/components/TopBar.vue';
import { onMounted, ref } from 'vue';
import API from '../../router/axios';
import 'bootstrap-icons/font/bootstrap-icons.css';
import approvedIcon from "../../assets/staticIcon/approved.svg";
import completedIcon from '../../assets/staticIcon/completed.svg';
import trainingIcon from '../../assets/staticIcon/training.svg';
import pendingIcon from '../../assets/staticIcon/pending.svg';
import rejectedIcon from '../../assets/staticIcon/rejected.svg';
import { ElDialog, ElMessage, ElSelect, ElInput, ElButton } from 'element-plus';
import { format } from 'date-fns';

const userid=localStorage.getItem('userID')
const reviewDialogVisible = ref(false)
const reviewId=ref(0);
// const uploadDialogVisible = ref(false)
let models = ref([])
let rejectedReason = ref('')
let value = ref('')
const options = [
  {
    value: 'approved',
    label: 'approved',
  },
  {
    value: 'rejected',
    label: 'rejected',
  }
]

onMounted(async () => {
  //查询参数传参方式，应对后端GET
  get_train_dataset_message();
});


const get_train_dataset_message = async () => {
    //查询参数传参方式，应对后端GET/DELETE
    try {
    const response = await API.get('data/admin/get_train_dataset_message/', {
      params: {
        userid: userid
      }
    });
    models.value = response.data.data;
    for (let i = 0; i < models.value.length; i++) {
      models.value[i].upload_time = format(new Date(models.value[i].upload_time), 'yyyy-MM-dd HH:mm:ss');
    }
  } catch (error) {
    let errorMessage = ref('An unknown error occurred');
    if (error.response.data.message) {
      errorMessage = error.response.data.message;
    }
    ElMessage.error(errorMessage.value);
  }
}
const get_oss_dataset = async (model) => {
  console.log('Downloading', model.dataset_id);
    //查询参数传参方式，应对后端GET/DELETE
    try {
    const response = await API.get('data/admin/get_oss_dataset/', {
      params: {
        userid: userid,
        dataset_id: model.dataset_id
      }
    });
    let url=response.data.dataset_url;
    window.open(url);
  } catch (error) {
    let errorMessage = ref('An unknown error occurred');
    if (error.response.data.message) {
      errorMessage = error.response.data.message;
    }
    ElMessage.error(errorMessage.value);
  }
}

const reviewDataset = async () => {
  if (value.value == 'rejected'&&rejectedReason.value == '') {
    ElMessage.error('Please enter the rejection reason');
  }else if(value.value == ''){
    ElMessage.error('Please select the review result');
  }else{
    console.log('Reviewing',reviewId.value);
    //请求体传参方式，应对后端POST/PATCH/PUT
    try {
      const response = await API.patch('/data/admin/review_train_dataset/', {
        "userid": userid,
        "dataset_id": reviewId.value,
        "is_qualified": value.value == 'approved' ? true : false,
        "rejection_reason": rejectedReason.value
      });
      let message = ref('');
      message.value = response.data.message;
      ElMessage.success(message.value);
      reviewDialogVisible.value = false;
      get_train_dataset_message();
    } catch (error) {
      let errorMessage = ref('An unknown error occurred');
      if (error.response.data.message) {
        errorMessage = error.response.data.message;
      }
      ElMessage.error(errorMessage.value);
    }
  }
}

const model_train = async (model) => {
  console.log('Training', model.dataset_id);
  //请求体传参方式，应对后端POST/PATCH/PUT
  try {
    await API.post('V2I_model/admin/train_model/', {
      "dataset_id": model.dataset_id
    });
    model.value.can_model_train = false;
    ElMessage.success("The training task has been submitted.");
    get_train_dataset_message();
  } catch (error) {
    let errorMessage = ref('An unknown error occurred');
    ElMessage.error(errorMessage.value);
  }
}

function getStateIcon(state) {
  switch (state.toLowerCase()) {
    case 'completed':
      return completedIcon;
    case 'training':
      return trainingIcon;
    case 'pending':
      return pendingIcon;
    case 'approved':
      return approvedIcon;
    case 'rejected':
      return rejectedIcon;
    default:
      return ''; // 默认情况返回空
  }
}



</script>

<style scoped>
.admin-container {
  height: 100vh;
  padding: 10px 20px;
}

.table-container {
  font-size: 17px;
  display: flex;
  width: 1200px;
  border: 4px solid #E5E5E5;
  border-radius: 20px;
  padding: 20px 20px 60px 20px;
  margin: 0 auto;
  flex-direction: column;
}

.header {
  width: 100%;
  display: flex;
  justify-content: end;
  padding-top: 10px;
  padding-right: 20px;
}

.table-container h1 {
  font-size: 36px;
  text-align: left;
  margin-top: 10px;
  margin-left: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #E5E5E5;
}

.upload-section {
  padding: 0px 40px 20px 40px;
  margin-top: 0px;
}

.upload-section h2 {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  text-align: center;
}

.uploadElement>>>.el-upload-dragger {
  border: 1px dashed #ddd;
  border-width: 3px 3px;
  border-radius: 12px;
  transition: border-color 0.1s;
}

.uploadElement>>>.el-upload-dragger:hover {
  border-color: #c6c6c6
}

.upload-dropzone {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.browse-button {
  margin-top: 10px;
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

.model-detail {
  display: flex;
  flex-direction: column;
  margin-top: -10px;
  margin-left: 20px;
  text-align: left;
}

.submit-section {
  margin-top: 20px;
  width: 100%;
  display: flex;
  justify-content: end
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

h2 {
  font-weight: bold;
  width: 80%;
  margin: 5% 10% 2% 10%;
  text-align: left;
}

table {
  width: 90%;
  margin: 0 auto;
}

th,
td {
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
  font-size: 14px;
  padding: 5px 10px;
  transition: background-color 0.3s ease;
}

.operation:disabled {
  background-color: #e0e0e0;
  color: #b0b0b0;
  cursor: not-allowed;
}

.operation:hover:not(:disabled) {
  background-color: #2f3640;
  color: white;
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

.state-icon {
  width: 80px;
  height: 30px;
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
</style>