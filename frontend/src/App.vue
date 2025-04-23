<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router';
</script>

<style>
/* 全局样式 */
body, html, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  font-family: Arial, sans-serif;
  box-sizing: border-box;
}

#app {
  text-align: center;
}

.router-view {
  flex: 1;
}
</style>