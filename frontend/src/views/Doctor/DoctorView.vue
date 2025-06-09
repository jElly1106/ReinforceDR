<template>
  <div class="doctor-panel-container">
    <div class="header-section">
      <h2 class="page-title">患者管理</h2>
      <div class="action-buttons">
        <el-button type="primary" @click="showAddDialog = true" icon="Plus">
          添加患者
        </el-button>
      </div>
    </div>

    <el-card class="patient-table-card" shadow="never">
      <el-table 
        :data="patients" 
        style="width: 100%"
        stripe
        v-loading="loading"
        empty-text="暂无患者数据"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="id" label="ID" width="80" sortable />
        <el-table-column prop="name" label="姓名" sortable />
        <el-table-column prop="gender" label="性别" width="100">
          <template #default="{row}">
            <el-tag :type="row.gender === '男' ? 'primary' : 'danger'" effect="plain">
              {{ row.gender }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="100" sortable />
        <el-table-column prop="phone" label="电话" />
        <el-table-column label="操作" width="400" fixed="right">
          <template #default="scope">
            <el-button size="medium" @click="viewDetail(scope.row.id)" icon="View" type="info" plain>
              详情
            </el-button>
            <el-button size="medium" @click="editPatient(scope.row)" icon="Edit" type="warning" plain>
              编辑
            </el-button>
            <el-popconfirm title="确定要删除此患者吗？" @confirm="deletePatient(scope.row.id)">
              <template #reference>
                <el-button size="medium" icon="Delete" type="danger" plain>
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container" v-if="patients.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalPatients"
          :page-sizes="[3, 5, 8, 10]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchPatients"
          @current-change="fetchPatients"
        />
      </div>
    </el-card>

    <!-- 添加/编辑患者对话框 -->
    <el-dialog 
      :title="isEdit ? '编辑患者信息' : '添加新患者'" 
      v-model="showAddDialog"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form 
        :model="form" 
        label-width="90px"
        :rules="rules"
        ref="patientForm"
        label-position="left"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入患者姓名" clearable />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="form.gender" placeholder="请选择性别" style="width: 100%">
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number 
            v-model="form.age" 
            :min="0" 
            :max="120" 
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系电话" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPatient">
          {{ isEdit ? '保存修改' : '确认添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage} from 'element-plus';
import API from '@/router/axios';

const patients = ref([]);
const showAddDialog = ref(false);
const isEdit = ref(false);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const totalPatients = ref(0);
const patientForm = ref(null);

const form = ref({
  id: null,
  name: '',
  gender: '',
  age: null,
  phone: ''
});

const rules = {
  name: [{ required: true, message: '请输入患者姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  age: [{ required: true, message: '请输入年龄', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ]
};

const fetchPatients = async () => {
  try {
    loading.value = true;
    const res = await API.get('/api/patient/my-patients', {
      params: {
        page: currentPage.value,
        pageSize: pageSize.value
      }
    });
    
    patients.value = res.data?.data?.items || [];
    totalPatients.value = res.data?.data?.total || 0;
  } catch (err) {
    console.error('获取患者失败', err);
    ElMessage.error('获取患者信息失败');
  } finally {
    loading.value = false;
  }
};

const handleSortChange = ({ prop, order }) => {
  console.log('排序字段:', prop, '排序方式:', order);
};

import { useRouter } from 'vue-router';

const router = useRouter();

const viewDetail = (id) => {
  router.push({ path: `/patient-detail/${id}` });
};

const editPatient = (patient) => {
  form.value = { ...patient };
  isEdit.value = true;
  showAddDialog.value = true;
};

const submitPatient = async () => {
  try {
    await patientForm.value.validate();
    
    loading.value = true;
    if (isEdit.value) {
      await API.put(`/api/patient/update-patient/${form.value.id}`, form.value);
      ElMessage.success('患者信息修改成功');
    } else {
      await API.post('/api/patient/add-patient', form.value);
      ElMessage.success('患者添加成功');
    }
    
    showAddDialog.value = false;
    isEdit.value = false;
    resetForm();
    fetchPatients();
  } catch (err) {
    if (!err.response) return;
    ElMessage.error(err.response?.data?.error || '操作失败');
  } finally {
    loading.value = false;
  }
};

const resetForm = () => {
  form.value = {
    id: null,
    name: '',
    gender: '',
    age: null,
    phone: ''
  };
};

const deletePatient = async (id) => {
  try {
    loading.value = true;
    await API.delete(`/api/patient/delete-patient/${id}`);
    ElMessage.success('患者删除成功');
    fetchPatients();
  } catch (err) {
    ElMessage.error('删除失败');
  } finally {
    loading.value = false;
  }
};

onMounted(fetchPatients);
</script>

<style scoped>
/* 全局字体进一步放大 */
* {
  font-size: 20px;
}

/* 页面容器 */
.doctor-panel-container {
  padding: 40px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 64px);
}

/* 顶部标题区 */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-title {
  color: #303133;
  font-weight: 700;
  font-size: 32px;
  margin: 0;
}

/* 操作按钮区域 */
.action-buttons {
  display: flex;
  gap: 20px;
}

.el-button {
  border-radius: 8px;
  font-size: 20px;
  padding: 12px 20px;
}

/* 表格卡片样式 */
.patient-table-card {
  border-radius: 12px;
  border: 1px solid #ebeef5;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 16px;
}

/* 表头加粗放大 */
:deep(.el-table__header) th {
  background-color: #f0f2f5;
  font-weight: 700;
  color: #333;
  font-size: 20px;
  height: 60px;
}

/* 表格行字体和高度 */
:deep(.el-table__row) {
  font-size: 20px;
  height: 60px;
}

/* 表单输入项字体放大 */
:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-form-item__label) {
  font-size: 20px;
}

:deep(.el-input__inner),
:deep(.el-select .el-input__inner),
:deep(.el-input-number .el-input__inner) {
  height: 48px;
  font-size: 20px;
}

:deep(.el-select-dropdown__item) {
  font-size: 20px;
}

:deep(.el-tag) {
  font-size: 18px;
  padding: 4px 10px;
}

/* 分页组件字体和尺寸放大 */
.pagination-container {
  margin-top: 28px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-pagination) {
  font-size: 20px;
}

:deep(.el-pagination button),
:deep(.el-pagination .el-pager li) {
  height: 40px;
  line-height: 40px;
  font-size: 20px;
}

/* 对话框内容放大 */
:deep(.el-dialog__body) {
  font-size: 20px;
  line-height: 1.8;
}

:deep(.el-dialog__title) {
  font-size: 24px;
  font-weight: bold;
}

</style>
