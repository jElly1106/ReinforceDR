<template>
    <div class="history">
      <h2>History of Retinal Image Segmentation</h2>
      
      <!-- 搜索框 -->
      <!-- <div class="search-box">
        <input type="text" v-model="searchQuery" placeholder="Search by description" @input="fetchHistory" />
      </div> -->
  
      <!-- 每页显示条数选择 -->
      <div class="page-size-selector">
        <label for="page-size">Items per page:</label>
        <select v-model="itemsPerPage" @change="fetchHistory">
          <option value="2">2</option>
          <option value="3">3</option>
          <option value="5">5</option>
          <option value="10">10</option>
        </select>
      </div>
      
      <!-- 显示历史记录 -->
      <div class="history-list">
        <div v-for="(item, index) in historyItems" :key="index" class="history-item">
          <img :src="item.image_path" alt="Image" class="history-image" />
          <div class="history-info">
            <h3>{{ item.image_name }}</h3>
            <p>{{ item.description }}</p>
            <p>Segmentation Status: {{ item.segmentation ? item.segmentation.status : 'Pending' }}</p>
            <button @click="viewSegmentationResult(item.segmentation ? item.segmentation.id : null)">
              View Segmentation Result
            </button>
          </div>
        </div>
      </div>
      
      <!-- 分页 -->
      <div class="pagination">
        <button @click="changePage(page - 1)" :disabled="page <= 1">Previous</button>
        <span>Page {{ page }} of {{ totalPages }}</span>
        <button @click="changePage(page + 1)" :disabled="page >= totalPages">Next</button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import API from '../../router/axios';
  
  const searchQuery = ref('');
  const historyItems = ref([]);
  const page = ref(1);
  const totalPages = ref(1);
  const itemsPerPage = ref(3);  // 每页显示记录数，默认是10
  
  const fetchHistory = async () => {
    try {
      const response = await API.get('/api/retinal/history', {
        params: {
          page: page.value,
          per_page: itemsPerPage.value,  // 使用当前每页条数
          search: searchQuery.value,  // 用来过滤描述的搜索
        },
      });
  
      const data = response.data;
      historyItems.value = data.data.items;
      totalPages.value = data.data.pages;
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };
  
  const changePage = (newPage) => {
    if (newPage < 1 || newPage > totalPages.value) return;
    page.value = newPage;
    fetchHistory(); // 每次切换页面重新获取数据
  };
  
  const viewSegmentationResult = (segmentationId) => {
    if (segmentationId) {
      // 跳转到查看分割结果的页面
      console.log('Viewing segmentation result for:', segmentationId);
      // 例如可以使用 Vue Router 跳转
      // this.$router.push({ name: 'segmentationResult', params: { id: segmentationId } });
    } else {
      alert('No segmentation result available yet');
    }
  };
  
  // 组件加载时请求历史记录
  onMounted(() => {
    fetchHistory();
  });
  </script>
  
  <style scoped>
  .history {
    padding: 20px;
  }
  
  .history h2 {
    font-size: 24px;
    margin-bottom: 20px;
  }
  
  .history-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .history-item {
    display: flex;
    gap: 20px;
    background-color: #f5f5f5;
    padding: 10px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .history-image {
    width: 100px;
    height: 100px;
    object-fit: cover;
    border-radius: 8px;
  }
  
  .history-info {
    flex: 1;
  }
  
  .search-box input {
    width: 200px;
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #ccc;
  }
  
  .page-size-selector {
    margin-bottom: 20px;
  }
  
  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
  
  .pagination button {
    padding: 10px;
    margin: 0 10px;
    border-radius: 4px;
    border: 1px solid #ccc;
    background-color: #fff;
    cursor: pointer;
  }
  
  .pagination button:disabled {
    cursor: not-allowed;
    background-color: #ddd;
  }
  </style>
  