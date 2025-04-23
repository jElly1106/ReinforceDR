<template>
    <div class="sum-container">
        <div class="left-container">
            <SideBar/>
        </div>
        <div class="right-container">
            <div class="header">
                <TopBar/>
            </div>
            <router-view></router-view>
        </div>
    </div>
</template>

<script setup>
import SideBar from '@/components/SideBar.vue';
import TopBar from '@/components/TopBar.vue';
</script>

<style scoped>
.sum-container{
    display: flex;
    flex-direction: row;
    height:100vh;
    width:100vw;
}
.left-container{
    width:200px;
}
.right-container{
    display: flex;
    flex-direction: column;
    /* 我滴妈，减号左右要有空格，稀奇 */
    width:calc(100% - 200px);
}
.header{
    width:calc(100% - 20px);
    display: flex;
    justify-content: end;
    padding-top:10px;
    padding-right:20px;
}
.router-view {
  padding: 20px;
  overflow-y: auto; 
}
</style>

