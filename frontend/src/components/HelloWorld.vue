<template>
  <div class="hello">
  {{ message }}
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import API from '../router/axios';
const message=ref();
const fetchBackendData = async () => {
  try {
    const response = await API.get('/account/hello');
    message.value = response.data;
  } catch (error) {
    message.value = error.response?.data?.message || 'An error occurred while fetching data.';
  }
};
onMounted(fetchBackendData);
</script>


