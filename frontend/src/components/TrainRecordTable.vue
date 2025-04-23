<template>
  <div class="main-container">
    <div class="best-epoch">
      <div ref="chartContainer1" style="height: 400px; width: 100%"></div>
      <div style="text-align: center; font-weight: bold;">BestEpoch</div>
    </div>
    <div class="accuracy">
      <div ref="chartContainer2" style="height: 400px; width: 100%"></div>
      <div style="text-align: center; font-weight: bold;">Accuracy</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch, defineProps } from 'vue';
import * as echarts from 'echarts';

// 定义 props 接收数据
const props = defineProps({
  bestEpochData: {
    type: Array,
    default: () => []
  },
  accuracyData: {
    type: Array,
    default: () => []
  }
});

const chartContainer1 = ref(null);
const chartContainer2 = ref(null);

onMounted(() => {
  if (props.bestEpochData && props.accuracyData) {
    renderChart();
  }
});

// 添加 watch 以响应数据变化
watch([() => props.bestEpochData, () => props.accuracyData], () => {
  if (props.bestEpochData && props.accuracyData) {
    renderChart();
  }
});

function renderChart() {
  const epochChart = echarts.init(chartContainer1.value);
  const accuracyChart = echarts.init(chartContainer2.value);

  // 限制最多显示50条数据
  const limitedBestEpochData = props.bestEpochData.slice(-50);

  // 使用限制后的数据
  const epochIndices = limitedBestEpochData.map(item => item.index);
  const linkStatuses = limitedBestEpochData.map(item => item.link_status);
  const top1Preds = limitedBestEpochData.map(item => item.top3_pred[0]);
  const top2Preds = limitedBestEpochData.map(item => item.top3_pred[1]);
  const top3Preds = limitedBestEpochData.map(item => item.top3_pred[2]);

  const accuracyIndices = props.accuracyData.map(item => item.epoch);
  const top1Accuracies = props.accuracyData.map(item => item.top1_accuracy);
  const top2Accuracies = props.accuracyData.map(item => item.top2_accuracy);
  const top3Accuracies = props.accuracyData.map(item => item.top3_accuracy);

  // 定义每个系列的数据
  const epochSeriesData = [
    {
      name: 'Link Status',
      type: 'line',
      data: linkStatuses,
      smooth: true,
      lineStyle: { color: '#787FE6' },
    },
    {
      name: 'Top1 Pred',
      type: 'scatter',
      data: epochIndices.map((index, i) => [index - 1, top1Preds[i]]),
      symbolSize: 10,
      itemStyle: { color: '#E95F5F' },
    },
    {
      name: 'Top2 Pred',
      type: 'scatter',
      data: epochIndices.map((index, i) => [index - 1, top2Preds[i]]),
      symbolSize: 10,
      itemStyle: { color: '#91cc75' },
    },
    {
      name: 'Top3 Pred',
      type: 'scatter',
      data: epochIndices.map((index, i) => [index - 1, top3Preds[i]]),
      symbolSize: 10,
      itemStyle: { color: '#FACD79' },
    },
  ];

  const accuracySeriesData = [
    {
      name: 'top1_accuracy',
      type: 'line',
      data: top1Accuracies,
      smooth: true,
    },
    {
      name: 'top2_accuracy',
      type: 'line',
      data: top2Accuracies,
      smooth: true,
    },
    {
      name: 'top3_accuracy',
      type: 'line',
      data: top3Accuracies,
      smooth: true,
    },
  ];

  const epochOption = {
    // title:{
    //   text: 'BestEpoch',
    // },
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['Link Status', 'Top1 Pred', 'Top2 Pred', 'Top3 Pred'],
    },
    xAxis: {
      type: 'category',
      data: epochIndices,
      name: 'Index',
    },
    yAxis: {
      type: 'value',
      name: 'Values',
    },
    series: epochSeriesData,
  };

  const accuracyOption = {
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['top1_accuracy', 'top2_accuracy', 'top3_accuracy'],
    },
    xAxis: {
      type: 'category',
      data: accuracyIndices,
      name: 'Epoch',
    },
    yAxis: {
      type: 'value',
      name: 'Accuracy',
    },
    series: accuracySeriesData,
  }

  epochChart.setOption(epochOption);
  accuracyChart.setOption(accuracyOption)
}
</script>

<style scoped>
.main-container{
  width: 100%;
}

.best-epoch{
  margin-top: 40px;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.accuracy{
  margin-top: 40px;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

</style>
