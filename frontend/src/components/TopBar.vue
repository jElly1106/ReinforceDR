<!-- 
 顶部导航栏
 暂时未处理图标一致性问题
  -->
<template>
  <div class="sidebar">
    <ul class="nav-list">
      <img src="../assets/staticIcon/setting.svg" class="icon" @click="logoutVisible=true"/>
    </ul>
  </div>

  <el-dialog v-model="logoutVisible" title=" " width="200" center >
    <button class="operation"  @click="logout">logout</button>
  </el-dialog>

</template>

<!-- 如果没有setup图标就引入出错,稀奇 -->
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
const router = useRouter();
const logoutVisible = ref(false);
const logout = () => {
  console.log('logout');
  localStorage.removeItem('access_token');
  localStorage.removeItem('userID');
  localStorage.removeItem('selectedStation');
  localStorage.removeItem('selectedStationName');
  router.push('/');
};
</script>

<style scoped>
.sidebar {
  user-select: none;
  height: 50px;
  background-color: #FFF;
}

.avatar {
  background-color: #630A45;
  border-radius: 50px;
  width: 30px;
  height: 30px;
  margin-right: 10px;
  cursor: pointer;
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


.nav-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: row;
}

.user {
  color: #333;
  margin-left: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.icon {
  margin-left: 20px;
  width: 30px;
  height: 30px;
  color: #252525;
  cursor: pointer;
}
</style>