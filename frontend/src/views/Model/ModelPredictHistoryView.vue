<template>
  <div class="history">
    <h2>History of Retinal Image Segmentation</h2>

    <div class="page-size-selector">
      <label for="page-size">Items per page:</label>
      <select v-model="itemsPerPage" @change="fetchHistory">
        <option value="2">2</option>
        <option value="3">3</option>
        <option value="5">5</option>
        <option value="10">10</option>
      </select>
    </div>
    
    <div class="history-list">
      <div v-for="(item, index) in historyItems" :key="index" class="history-item">
        <div class="image-container">
          <img :src="item.image_url" alt="Image" class="history-image" />
        </div>
        <div class="history-info">
          <h3>{{ item.image_name }}</h3>
          <p class="description">{{ item.description }}</p>
          <p class="status">Segmentation Status: {{ item.segmentation ? item.segmentation.status : 'Pending' }}</p>
          <button class="view-btn" @click="viewSegmentationResult(item.segmentation ? item.segmentation.id : null)">
            View Segmentation Result
          </button>
        </div>
      </div>
    </div>
    
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
  import { useRouter } from 'vue-router';
  const router = useRouter();
  
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
      router.push({
        name: 'segmentationResult',
        params: { id: segmentationId }
      });
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
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.history h2 {
  font-size: 2rem;
  text-align: center;
  margin-bottom: 2rem;
  color: #2c3e50;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 1rem 0;
}

.history-item {
  display: flex;
  gap: 2rem;
  background-color: #ffffff;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.history-item:hover {
  transform: translateY(-2px);
}

.image-container {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
}

.history-image {
  max-width: 300px;
  max-height: 200px;
  object-fit: contain;
  border-radius: 6px;
}

.history-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.history-info h3 {
  font-size: 1.4rem;
  color: #34495e;
  margin: 0;
}

.description {
  color: #7f8c8d;
  line-height: 1.6;
  margin: 0;
}

.status, .view-btn {
  margin-left: 100px;
  align-self: flex-start;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.status {
  color: #87149e;
  font-weight: 500;
  background-color: transparent; /* 保留原本透明背景 */
}

.view-btn {
  background-color: #7f34db;
  color: white;
}

.view-btn:hover {
  background-color: #2980b9;
}

.page-size-selector {
  text-align: center;
  margin-bottom: 2rem;
}

.page-size-selector label {
  margin-right: 0.8rem;
  color: #34495e;
}

.page-size-selector select {
  padding: 0.5rem;
  border-radius: 6px;
  border: 1px solid #bdc3c7;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.pagination button {
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  border: 1px solid #3498db;
  background-color: #3498db;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination button:disabled {
  background-color: #bdc3c7;
  border-color: #bdc3c7;
  cursor: not-allowed;
}

.pagination button:not(:disabled):hover {
  background-color: #2980b9;
  border-color: #2980b9;
}

.pagination span {
  color: #34495e;
  font-weight: 500;
}

@media (max-width: 768px) {
  .history-item {
    flex-direction: column;
    padding: 1.5rem;
  }

  .image-container {
    padding: 0.5rem;
  }

  .history-image {
    max-width: 100%;
    height: auto;
  }

  .view-btn {
    align-self: stretch;
    text-align: center;
  }
}
  </style>
  