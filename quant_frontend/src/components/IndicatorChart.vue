<template>
  <div>
    <div v-if="!props.indicators || !props.indicators.dates || props.indicators.dates.length === 0" 
         class="chart-area flex items-center justify-center min-h-[200px] text-gray-400 text-lg no-data-message"
         data-cy="no-data-message">
      暂无数据
    </div>
    <div v-else ref="chartRef" class="chart-area chart-container has-data" style="width: 100%; min-height: 900px; padding-bottom: 32px;" data-cy="indicator-chart"></div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, computed } from 'vue';
import * as echarts from 'echarts/core';
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  MarkPointComponent,
  MarkLineComponent,
  TitleComponent,
} from 'echarts/components';
import { CandlestickChart, LineChart, BarChart } from 'echarts/charts';
import { UniversalTransition } from 'echarts/features';
import { CanvasRenderer } from 'echarts/renderers';
import type { EChartsOption, SeriesOption as EchartsSeriesOption, XAXisComponentOption, YAXisComponentOption } from 'echarts';
import type { PropType } from 'vue';

echarts.use([
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  MarkPointComponent,
  MarkLineComponent,
  CandlestickChart,
  LineChart,
  BarChart,
  UniversalTransition,
  CanvasRenderer,
  TitleComponent,
]);

interface IndicatorData {
  dates: string[];
  open?: number[];
  close: number[];
  low?: number[];
  high?: number[];
  volume: number[];
  obv?: number[];
  vma_5?: number[];
  vr?: number[];
  mfi?: number[];
  pma_5?: number[];
  pma_20?: number[];
  pma_60?: number[];
  [key: string]: any;
}

const props = defineProps({
  indicators: {
    type: Object as PropType<IndicatorData | null>,
    required: true,
  },
  title: {
    type: String,
    default: '行情与指标',
  },
});

const chartRef = ref<HTMLElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

const EMPTY_CHART_OPTION: EChartsOption = {
  title: {
    text: props.title,
    left: 'center',
  },
  legend: { data: [] },
  xAxis: { type: 'category', data: [] } as XAXisComponentOption,
  yAxis: { type: 'value' } as YAXisComponentOption,
  series: [],
};

const chartOption = computed<EChartsOption>(() => {
  if (!props.indicators || !props.indicators.dates || props.indicators.dates.length === 0) {
    return { ...EMPTY_CHART_OPTION, title: { text: props.title, left: 'center' } };
  }

  const indicatorsData = props.indicators;
  const dates = indicatorsData.dates;
  
  const klineData = dates.map((_, i) => [
    indicatorsData.open?.[i] ?? indicatorsData.close[i],
    indicatorsData.close[i] ?? 0,
    indicatorsData.low?.[i] ?? indicatorsData.close[i],
    indicatorsData.high?.[i] ?? indicatorsData.close[i],
    indicatorsData.volume?.[i] ?? 0,
  ]);

  const pmaSeriesList: EchartsSeriesOption[] = [];
  const vmaSeriesList: EchartsSeriesOption[] = [];
  const legendData: string[] = [];
  
  if (indicatorsData.open && indicatorsData.close && indicatorsData.low && indicatorsData.high) {
    legendData.push('K线');
  }
  legendData.push('成交量');

  Object.keys(indicatorsData).forEach(key => {
    if (key.startsWith('pma_')) {
      const window = key.split('_')[1];
      pmaSeriesList.push({
        name: `PMA${window}`,
        type: 'line',
        data: indicatorsData[key],
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 1.5 },
        xAxisIndex: 0,
        yAxisIndex: 0,
        gridIndex: 0,
      } as EchartsSeriesOption);
      legendData.push(`PMA${window}`);
    } else if (key.startsWith('vma_')) {
      const window = key.split('_')[1];
      vmaSeriesList.push({
        name: `VMA${window}`,
        type: 'line',
        data: indicatorsData[key],
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 1.5 },
        xAxisIndex: 2,
        yAxisIndex: 3,
        gridIndex: 2,
      } as EchartsSeriesOption);
      legendData.push(`VMA${window}`);
    }
  });
  
  if (indicatorsData.obv) {
    legendData.push('OBV');
  }
  if (indicatorsData.vr) {
    legendData.push('VR');
  }
  if (indicatorsData.mfi) {
    legendData.push('MFI');
  }

  const seriesArray: EchartsSeriesOption[] = [];

  if (indicatorsData.open && indicatorsData.close && indicatorsData.low && indicatorsData.high) {
    seriesArray.push({
      name: 'K线',
      type: 'candlestick',
      data: klineData.map(item => [item[0], item[1], item[2], item[3]]),
      itemStyle: {
        color: '#ec0000',
        color0: '#00da3c',
        borderColor: '#8A0000',
        borderColor0: '#008F28',
      },
      xAxisIndex: 0,
      yAxisIndex: 0,
      gridIndex: 0,
    } as EchartsSeriesOption);
  }

  seriesArray.push({
    name: '成交量',
    type: 'bar',
    data: klineData.map(item => item[4]),
    xAxisIndex: 0,
    yAxisIndex: 1,
    gridIndex: 0,
    itemStyle: {
      color: (params: any) => {
        const currentData = klineData[params.dataIndex];
        if (currentData && typeof currentData[1] === 'number' && typeof currentData[0] === 'number') {
          return currentData[1] >= currentData[0] ? '#ef232a' : '#14b143';
        }
        return '#ccc';
      }
    },
  } as EchartsSeriesOption);

  seriesArray.push(...pmaSeriesList);

  if (indicatorsData.obv) {
    seriesArray.push({
      name: 'OBV',
      type: 'line',
      data: indicatorsData.obv,
      smooth: true,
      showSymbol: false,
      lineStyle: { width: 1.5 },
      xAxisIndex: 1,
      yAxisIndex: 2,
      gridIndex: 1,
    } as EchartsSeriesOption);
  }

  seriesArray.push(...vmaSeriesList);

  if (indicatorsData.vr) {
    seriesArray.push({
      name: 'VR',
      type: 'line',
      data: indicatorsData.vr,
      smooth: true,
      showSymbol: false,
      lineStyle: { width: 1.5 },
      xAxisIndex: 3,
      yAxisIndex: 4,
      gridIndex: 3,
    } as EchartsSeriesOption);
  }

  if (indicatorsData.mfi) {
    seriesArray.push({
      name: 'MFI',
      type: 'line',
      data: indicatorsData.mfi,
      smooth: true,
      showSymbol: false,
      lineStyle: { width: 1.5 },
      xAxisIndex: 4,
      yAxisIndex: 5,
      gridIndex: 4,
    } as EchartsSeriesOption);
  }

  const gridHeight = 12;
  const mainChartHeight = 100 - 15 - (gridHeight * 4) - 10;

  return {
    title: {
      text: props.title,
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
      confine: true,
      backgroundColor: '#fff',
      borderColor: '#eee',
      borderWidth: 1,
      textStyle: { color: '#333' },
    },
    legend: {
      data: legendData,
      bottom: 10,
      left: 'center',
      type: 'scroll',
      itemWidth: 18,
      itemHeight: 12,
      textStyle: { fontSize: 13 },
      selectedMode: 'multiple',
    },
    grid: [
      { left: '8%', right: '8%', top: '8%', height: `${mainChartHeight}%`, containLabel: false },
      { left: '8%', right: '8%', top: `${8 + mainChartHeight + 3}%`, height: `${gridHeight}%`, containLabel: false },
      { left: '8%', right: '8%', top: `${8 + mainChartHeight + 3 + gridHeight + 3}%`, height: `${gridHeight}%`, containLabel: false },
      { left: '8%', right: '8%', top: `${8 + mainChartHeight + 3 + (gridHeight * 2) + 6}%`, height: `${gridHeight}%`, containLabel: false },
      { left: '8%', right: '8%', top: `${8 + mainChartHeight + 3 + (gridHeight * 3) + 9}%`, height: `${gridHeight}%`, containLabel: false },
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax',
        gridIndex: 0,
      },
      {
        type: 'category',
        data: dates,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax',
        gridIndex: 1,
        axisLabel: { show: false },
        axisTick: { show: false },
      },
      {
        type: 'category',
        data: dates,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax',
        gridIndex: 2,
        axisLabel: { show: false },
        axisTick: { show: false },
      },
      {
        type: 'category',
        data: dates,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax',
        gridIndex: 3,
        axisLabel: { show: false },
        axisTick: { show: false },
      },
      {
        type: 'category',
        data: dates,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax',
        gridIndex: 4,
        axisLabel: { show: false },
        axisTick: { show: false },
      },
    ] as XAXisComponentOption[],
    yAxis: [
      {
        type: 'value',
        scale: true,
        name: '价格',
        splitArea: { show: true },
        gridIndex: 0,
        splitLine: { show: true },
        axisLabel: { color: '#333', fontSize: 12 },
      },
      {
        type: 'value',
        scale: true,
        name: '成交量',
        position: 'right',
        gridIndex: 0,
        axisLabel: { formatter: (value: number) => value > 10000 ? (value / 10000).toFixed(1) + 'w' : String(value), color: '#333', fontSize: 12 },
        splitLine: { show: false },
        axisLine: { show: true },
        axisTick: { show: true },
      },
      {
        type: 'value',
        scale: true,
        name: 'OBV',
        gridIndex: 1,
        splitLine: { show: true },
        axisLabel: {formatter: (value: number) => value > 1000000 ? (value/1000000).toFixed(1) + 'm' : (value > 1000 ? (value/1000).toFixed(1) + 'k' : String(value)), color: '#333', fontSize: 12}
      },
      {
        type: 'value',
        scale: true,
        name: 'VMA',
        gridIndex: 2,
        splitLine: { show: true },
        axisLabel: {formatter: (value: number) => value > 1000000 ? (value/1000000).toFixed(1) + 'm' : (value > 1000 ? (value/1000).toFixed(1) + 'k' : String(value)), color: '#333', fontSize: 12}
      },
      {
        type: 'value',
        scale: true,
        name: 'VR',
        gridIndex: 3,
        splitLine: { show: true },
        axisLabel: {formatter: (value: number) => parseFloat(value.toFixed(2)), color: '#333', fontSize: 12 }
      },
      {
        type: 'value',
        scale: true,
        name: 'MFI',
        gridIndex: 4,
        splitLine: { show: true },
        min: 0,
        max: 100,
        axisLabel: { color: '#333', fontSize: 12 },
      },
    ] as YAXisComponentOption[],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1, 2, 3, 4],
        start: 70,
        end: 100,
      },
      {
        show: true,
        xAxisIndex: [0, 1, 2, 3, 4],
        type: 'slider',
        bottom: 10,
        start: 70,
        end: 100,
        height: 24,
        borderColor: '#eee',
        backgroundColor: '#fafafa',
        fillerColor: '#e0e7ef',
        handleIcon: 'M8.7,11.2v-0.5c0-0.2-0.1-0.3-0.3-0.3H7.6c-0.2,0-0.3,0.1-0.3,0.3v0.5c0,0.2,0.1,0.3,0.3,0.3h0.8C8.6,11.5,8.7,11.4,8.7,11.2z',
        handleSize: '120%',
      },
    ],
    series: seriesArray,
  };
});

const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value);
    chartInstance.setOption(chartOption.value);
  }
};

const resizeChart = () => {
  chartInstance?.resize();
};

onMounted(() => {
  initChart();
  window.addEventListener('resize', resizeChart);
});

watch(() => props.indicators, (newVal, oldVal) => {
  if (chartInstance && newVal && newVal.dates && newVal.dates.length > 0) {
    if (JSON.stringify(newVal) !== JSON.stringify(oldVal)) {
      chartInstance.setOption(chartOption.value, { notMerge: false });
    }
  } else if (chartInstance) {
    chartInstance.clear();
    chartInstance.setOption({ ...EMPTY_CHART_OPTION, title: { text: props.title, left: 'center' } });
  }
}, { deep: true });

watch(() => props.title, () => {
  if (chartInstance) {
    chartInstance.setOption({ title: { text: props.title, left: 'center' } });
  }
});

</script>

<style scoped>
.chart-container {
  width: 100%;
  min-height: 900px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding-bottom: 32px;
}
</style> 