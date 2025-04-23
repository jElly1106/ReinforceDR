<template>
    <Stationlist />
    <div class="map-container">
        <Predictmap ref="predictmapRef" />
    </div>
</template>

<script setup>
import Predictmap from "../../components/PredictMap.vue"
import Stationlist from "../../components/BaseStation.vue"
// import { onMounted, ref } from 'vue';
// const predictmapRef = ref(null);

// onMounted(() => {
//     updateMap();
//   })
  
//   function updateMap() {
//     const selectedStation = localStorage.getItem('selectedStation');

//     if (predictmapRef.value) {
//         predictmapRef.value.fetchLocations(selectedStation);
//     } else {
//       console.error("Predictmap component is not found");
//     }
//   }

</script>

<style scoped>
.map-container{
    height: calc(100vh - 110px);
    overflow: hidden;
    border-radius: 8px; 
    margin: 25px;
}
</style>