<template>
    <div class="station-select">
      <el-select 
        v-model="selectedStation" 
        @change="stationChanged"
        placeholder="Base Station" 
        class="station-dropdown">
        
        <el-option
          v-for="station in stationList"
          :key="station.base_station_id"
          :label="station.base_station_name"
          :value="station.base_station_id">
        </el-option>
      </el-select>
    </div>
  </template>
  
  <script>
  import API from '../router/axios';
  
  export default {
    data() {
      return {
        selectedStation: null,
        stationList: [],
      };
    },
    methods: {
      async fetchStations() {
        try {
          const userId = localStorage.getItem('userID');
          const response = await API.get('/data/base_stations/my/', { params: { user_id: userId } });
          if (response.status === 200) {
            this.stationList = response.data;
          } else {
          }
        } catch (error) {
          console.error("Error fetching stations:", error);
        }
      },
      stationChanged(stationId) {
        stationId=1;
        this.$emit('station-selected', stationId);
      }
    },
    mounted() {
      this.fetchStations();
    }
  };
  </script>
  
  <style scoped>
  .station-select {
    position: absolute;
    top: 12px;
    right: 280px;
    display: flex;
    align-items: center;
  }
  
  .station-dropdown {
    width: 160px;
  }
  
  :deep(.el-select__placeholder)  {
    color: #555;
    font-size: 16px;
  }
  
  :deep(.el-select__wrapper) {
    box-shadow: 0 0 0 1px #ffffff inset;
  }
  
  :deep(.el-select__wrapper.is-hovering:not(.is-focused)) {
    box-shadow: 0 0 0 1px #ffffff inset;
  }
  
  :deep(.el-select__selection) {
    font-size: 16px;
    font-weight: 600;
  } 
  
  .custom-option {
    font-size: 14px;
    font-weight: 500;
  }
  </style>