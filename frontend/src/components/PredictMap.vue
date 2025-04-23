<template>
  <div>
    <div class="header">
      <div class="header-left">
        <img @click="navigateBack" class="back-arrow" src="@/assets/staticIcon/back.svg" alt="返回箭头" />
        <span class="title">Prediction History</span>
      </div>
      <div class="header-right">
        <label for="start-date">start-date</label>
        <input
          type="text"
          id="start-date"
          v-model="startDate"
          class="datepicker"
          placeholder="选择起始日期"
        />
        <label for="end-date">end-date</label>
        <input
          type="text"
          id="end-date"
          v-model="endDate"
          class="datepicker"
          placeholder="选择结束日期"
        />
        <button @click="filterData">filterData</button>
      </div>
    </div>

    <div ref="mapRef" class="map"></div>
    <div v-if="activeMarker" class="custom-info">
      坐标: {{ activeMarker.lat }}, {{ activeMarker.lng }}
    </div>
  </div>
</template>

<script setup>
/* global google */
import { ref, onMounted } from 'vue';  
import API from '../router/axios';
import { Loader } from '@googlemaps/js-api-loader';
import flatpickr from 'flatpickr';
import 'flatpickr/dist/flatpickr.css';
import { useRouter } from 'vue-router';

const router = useRouter();

const startDate = ref('');
const endDate = ref('');
const mapRef = ref(null);
const activeMarker = ref(null);
const locations = ref([]);
const filteredLocations = ref([]);
let markers = [];
let basestationMarker = null;

const navigateBack = () => {
  router.push({ name: 'modelpredict' });
};

const defaultLocation = { lat: 40.7128, lng: -74.0060 };

const createMarker = (lat, lng, map) => {
  return new google.maps.Marker({
    position: { lat, lng },
    map: map,
    icon: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
  });
};

const setMapCenter = (lat, lng) => {
  mapRef.value.map.setCenter({ lat, lng });
};

const handleError = (error) => {
  console.error('Error:', error);
  alert('An error occurred while fetching data');
  setMapCenter(defaultLocation.lat, defaultLocation.lng);
  if (basestationMarker) basestationMarker.setMap(null);
  basestationMarker = createMarker(defaultLocation.lat, defaultLocation.lng, mapRef.value.map);
};

const fetchLocations = async () => {
  const selectedStation = localStorage.getItem('selectedStation');

  const baseStationId = parseInt(selectedStation, 10);

  try {
    const response = await API.get('/data/get_all_device/', { 
      params: { base_station_id: baseStationId }
    });

    if (response.data.status === 'success') {
      const basestationGPS = response.data.data.basestation_GPS;
      locations.value = response.data.data.devices_GPS.map(item => ({
        lat: item.latitude,
        lng: item.longitude,
        date: new Date(item.capture_time).toLocaleDateString()
      }));

      filteredLocations.value = locations.value;

      if (basestationGPS) {
        setMapCenter(basestationGPS.latitude, basestationGPS.longitude);

        if (basestationMarker) basestationMarker.setMap(null);
        basestationMarker = createMarker(basestationGPS.latitude, basestationGPS.longitude, mapRef.value.map);
      } else {
        setMapCenter(defaultLocation.lat, defaultLocation.lng);
        if (basestationMarker) basestationMarker.setMap(null);
        basestationMarker = createMarker(defaultLocation.lat, defaultLocation.lng, mapRef.value.map);
        alert('No base station GPS data found');
      }

      console.log(response.data); 
      updateMarkers();
    } else {
      alert('Error: ' + response.data.message);
    }
  } catch (error) {
    handleError(error);
  }
};

const filterData = () => {
  const today = new Date();
  const todayStr = today.toISOString().split('T')[0];

  if (!endDate.value) {
    endDate.value = todayStr;
  }

  if (!startDate.value) {
    startDate.value = todayStr;
  }

  const selectedStartDate = new Date(startDate.value);
  const selectedEndDate = new Date(endDate.value);
  if (selectedEndDate > today) {
    endDate.value = todayStr;
  }
  if (selectedStartDate > today) {
    startDate.value = todayStr;
  }

  filteredLocations.value = locations.value.filter(location => {
    const locationDate = new Date(location.date); 
    const start = new Date(startDate.value); 
    const end = new Date(endDate.value);

    return locationDate >= start && locationDate <= end;
  });


  updateMarkers();
};

const updateMarkers = () => {
  if (!mapRef.value.map) {
    console.error('Map is not initialized');
    return;
  }

  markers.forEach(marker => marker.setMap(null));
  markers = [];

  filteredLocations.value.forEach(location => {
    const marker = new google.maps.Marker({
      position: { lat: location.lat, lng: location.lng },
      map: mapRef.value.map,
      icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
    });

    markers.push(marker);

    marker.addListener('mouseover', () => {
      activeMarker.value = location;
    });

    marker.addListener('mouseout', () => {
      activeMarker.value = null;
    });
  });
};

onMounted(() => {
  const loader = new Loader({
    apiKey: 'AIzaSyDUpZ5vnpgfkqz0F6xrFiVy2LWJJeRd8w4',
    version: 'weekly',
  });

  loader.load().then(() => {
    const map = new google.maps.Map(mapRef.value, {
      center: { lat: 0, lng: 0 },  // 初始位置，随后会被基站中心替代
      zoom: 15,
      zoomControl: false,
      streetViewControl: false,
      fullscreenControl: false,
    });

    mapRef.value.map = map;
    fetchLocations();

    flatpickr('#start-date', {
      enableTime: true,  // 启用时间选择
      dateFormat: "Y-m-d H:i",  // 格式化为年月日 时分
      onChange: (selectedDates) => {
        startDate.value = selectedDates[0] ? selectedDates[0].toISOString() : '';
      },
    });

    flatpickr('#end-date', {
      enableTime: true,  // 启用时间选择
      dateFormat: "Y-m-d H:i",  // 格式化为年月日 时分
      onChange: (selectedDates) => {
        endDate.value = selectedDates[0] ? selectedDates[0].toISOString() : '';
      },
    });
  });
});
</script>


<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between; 
  padding: 10px 20px;
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0; 
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); 
  z-index: 1000;
  position: sticky;
  top: 0;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
}

.back-arrow {
  width: 35px;
  height: 35px;
  margin-right: 22px;
  cursor: pointer;
}

.title {
  font-size: 30px;
  font-weight: bold;
  color: #000;
}

.header-right {
  display: flex; 
  align-items: center;
}

.header-right label {
  margin-right: 20px;
  font-size: 18px;
  font-weight: bold;
  color: #000;
  margin-left: 20px;
}

.header-right .datepicker {
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-right: 10px;
  font-size: 14px;
  background-color: #fafafa;
  color: #000;
}

.header-right .datepicker::placeholder {
  color: #aaa;
}

.header-right button {
  padding: 6px 12px;
  background-color: #000; 
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: background-color 0.2s ease;
  margin-left: 60px;
  margin-right: 30px;
}

.header-right button:hover {
  background-color: #444; 
}

.map {
  height: calc(100vh - 60px); 
  width: 100%;
  border-radius: 12px;
}

.custom-info {
  background: white;
  border: 1px solid black;
  padding: 5px;
  border-radius: 5px;
  position: fixed;
  bottom: 30px;
  left: 240px;
  z-index: 1000;
}

.datepicker:focus {
  outline: none;
  box-shadow: none;
  border-color: #ccc;
}
</style>