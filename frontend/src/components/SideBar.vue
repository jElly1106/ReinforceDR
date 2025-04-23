<!-- 
 侧边导航栏
 暂时未处理图标一致性以及图标点击后变化问题
  -->
<template>
  <div class="sidebar">
    <img src="../assets/staticIcon/Logo2.svg" class="logo"/>
    <ul class="nav-list">
      <li><router-link to="/sum/home" class="nav-item" active-class="active-nav-item" @click="getinfo">
        <img class="icon" :src="$route.path=='/sum/home'?'/icon/home.fill.svg':'/icon/home.svg'"/>
        Home</router-link></li>
      <li><router-link
          to="/sum/modelpredict"
          class="nav-item"
          :class="{ 'active-nav-item': $route.path.startsWith('/sum/modelpredict') }"
        >
          <img class="icon" :src="$route.path.startsWith('/sum/modelpredict') ? '/icon/predict.fill.svg' : '/icon/predict.svg'"/>
          Predict
        </router-link>
      </li>
      <li><router-link
          to="/sum/ai"
          class="nav-item"
          :class="{ 'active-nav-item': $route.path.startsWith('/sum/ai') }"
        >
          <img class="icon" :src="$route.path.startsWith('/sum/ai') ? '/icon/train.fill.svg' : '/icon/train.svg'"/>
          Consultation
        </router-link>
      </li>
      <li><router-link to="/sum/history" class="nav-item" active-class="active-nav-item">
        <img class="icon" :src="$route.path=='/sum/history'?'/icon/test.fill.svg':'/icon/test.svg'"/>
        History</router-link></li>
      <!-- <li><router-link to="/" class="nav-item" active-class="active-nav-item">
        <img class="icon" :src="$route.path=='/'?'/icon/document.fill.svg':'/icon/document.svg'"/>
        Documents</router-link></li> -->
    </ul>
  </div>

</template>

<!-- 如果没有setup图标就引入出错,稀奇 -->
<script setup>
import { useRoute } from 'vue-router';
// import {ref} from 'vue'
const route =useRoute();
const getinfo=()=>{
  console.log(route.path)
}
</script>
<style scoped>
.logo{
  color:#0E0E0E;
  width:60px;
  height:60px;
  display: flex; 
  align-items: center; 
  justify-content: center;
  font-size: 18px;
  margin:20px 70px 40px 70px;
}
.sidebar {
  width: 200px;
  height: 100vh;
  border-right:2px solid rgba(112, 94, 120,0.3);
  background-color: #FFF;

  display: flex;
  flex-direction: column; 
}

.nav-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  color:#333;
  text-decoration: none;
  padding-top:9px;
  padding-bottom:9px;
  padding-left:25px;

  display: flex; 
  align-items: center; 
  font-size: 18px;
}

.nav-item:hover {
  background-color: #FCFCFC; 
}

.active-nav-item{
  background-color: #FCFCFC; 
  border-left:2px solid #705E78;
}

.icon{
  width:27px;
  height:27px;
  margin-right:10px;
  color:#252525;
}
</style>
