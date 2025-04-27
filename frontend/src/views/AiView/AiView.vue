<template>
  <div class="app">
    <el-container style="min-height: 100vh">
  
      <el-main>
        <div class="header">
          <h2 class="title">线上问诊平台</h2>
          <p class="subtitle">提供便捷的问诊体验，支持上传症状描述和病历资料。</p>
        </div>
  
        <el-tabs v-model="activeTab" class="tabs">
          <el-tab-pane label="填写信息" name="consult">
            <el-card>
              <h3>患者信息</h3>
              <el-input v-model="form.name" placeholder="姓名" class="mb" />
              <el-input v-model="form.age" type="number" placeholder="年龄" class="mb" />
              <el-input
                v-model="form.symptoms"
                type="textarea"
                :rows="4"
                placeholder="描述您的症状..."
                class="mb"
              />
              <div class="upload-section">
                <h2 style="text-align: left; margin-top: -10px">Upload Data</h2>
                <h2 style="text-align: left; font-size:16px; margin-top: -10px">Please upload your medical files</h2>
                <el-upload
                  ref="uploadDom"
                  action="http://localhost:5000/multimodal"
                  :on-success="handleUploadSuccess"
                  :on-error="handleUploadError"
                  :file-list="fileList"
                  :auto-upload="false"
                  multiple
                  drag
                  accept=".png,.jpg,.jpeg,.bmp,.tif,.tiff"
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
              </div>
              <el-button type="primary" @click="submitForm">提交问诊</el-button>
            </el-card>
          </el-tab-pane>
  
          <el-tab-pane label="查看记录" name="records">
            <el-card>
              <h3>问诊记录（示例）</h3>
              <ul>
                <li v-for="(record, index) in records" :key="index">{{ record }}</li>
              </ul>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const activeTab = ref('consult')
const form = ref({
  name: '',
  age: '',
  symptoms: ''
})

const fileList = ref([]) // 文件列表
const records = ref([
  '2025-04-20：感冒症状，已开药',
  '2025-03-15：腰痛，建议复查',
  '2025-01-05：皮疹，开具皮肤科建议'
])

const handleUploadSuccess = (response) => {
  console.log('上传成功', response)
}

const handleUploadError = (error) => {
  console.error('上传失败', error)
}

const submitForm = async () => {
  if (!form.value.name || !form.value.symptoms) {
    return alert('请填写完整信息')
  }
  // 校验文件是否上传
  if (fileList.value.length === 0) {
    return alert('请上传病历或症状文件')
  }

  // 处理上传的数据
  const formData = new FormData()
  formData.append('name', form.value.name)
  formData.append('age', form.value.age)
  formData.append('symptoms', form.value.symptoms)

  fileList.value.forEach((file) => {
    formData.append('files[]', file.raw) // 将文件添加到 formData
  })

  try {
    // 提交表单数据到后端
    const response = await fetch('http://localhost:5000/multimodal', {
      method: 'POST',
      body: formData
    })
    const result = await response.json()
    if (result.error) {
      alert(result.error)
    } else {
      // 如果提交成功，跳转到 AI 聊天界面
      router.push('/sum/ai/chat')
    }
  } catch (err) {
    console.error('提交失败', err)
    alert('提交失败，请稍后再试')
  }
}
</script>

<style scoped>
/* 同原来的样式 */
.app {
  font-family: 'Segoe UI', sans-serif;
  height: 100vh;
}

/* 侧边栏调整 */
.aside {
  border-right: 1px solid #eee;
  padding: 24px 0;
  display: flex;
  flex-direction: column;
}

.logo {
  padding: 0 20px;
  margin-bottom: 40px;
}

.logo-icon {
  width: 64px;
  height: 64px;
  font-size: 32px;
  background-color: #66003d;
}

.logo h1 {
  font-size: 24px;
  margin-top: 16px;
}

/* 菜单项放大 */
.el-menu {
  flex: 1;
}

.el-menu-item {
  height: 56px !important;
  font-size: 16px;
}

.el-menu-item [class^="el-icon"] {
  font-size: 20px;
  margin-right: 12px;
}

/* 主内容区调整 */
.el-main {
  padding: 0 40px 40px;
}

.header {
  padding: 32px 0 24px;
}

.title {
  color: #66003d;
  font-size: 28px;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 16px;
  line-height: 1.6;
}

/* 标签页调整 */
.tabs {
  margin-top: 16px;
}

:deep(.el-tabs__item) {
  font-size: 18px !important;
  height: 48px !important;
}

.el-card h3 {
  font-size: 20px;
  margin-bottom: 32px;  /* 标题下方间距加大 */
}

/* 输入项间距调整 */
.mb {
  margin-bottom: 24px !important;  /* 从16px增加到24px */
}

/* 文本域额外间距 */
:deep(.el-textarea__inner) {
  margin-top: 8px;  /* 增加文本域顶部间距 */
}

/* 按钮上方增加间距 */
.el-button {
  margin-top: 16px;  /* 新增按钮顶部间距 */
}

/* 调整输入框内部间距 */
:deep(.el-input__inner) {
  padding: 0 20px !important;  /* 左右内间距加大 */
}

/* 增加卡片整体间距 */
.el-card {
  padding: 32px !important;  /* 卡片内边距增大 */
}

/* 按钮放大 */
.el-button {
  width: 100%;
  height: 48px;
  font-size: 16px !important;
}

/* 问诊记录列表 */
ul {
  padding-left: 20px;
}

li {
  font-size: 16px;
  line-height: 1.8;
  margin: 12px 0;
}
</style>
