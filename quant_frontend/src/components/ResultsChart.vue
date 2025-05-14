<template>
  <div class="p-4 bg-white rounded-lg shadow">
    <h2 class="text-xl font-bold mb-4">回测结果可视化</h2>
    
    <div 
      v-if="results && results.chart_data" 
      ref="chartContainerRef" 
      class="w-full chart-container"
      style="min-height: 600px; min-width: 300px; height: 70vh;"
    ></div>
    
    <div v-else class="flex items-center justify-center chart-container bg-gray-50 rounded-lg">
      <p class="text-gray-500">请先运行回测以查看图表</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, CandlestickChart } from 'echarts/charts';
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  MarkPointComponent,
  TitleComponent,
} from 'echarts/components';
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';

// 注册必要的组件
echarts.use([
  CanvasRenderer, 
  LineChart, 
  CandlestickChart, 
  GridComponent, 
  TooltipComponent, 
  LegendComponent, 
  DataZoomComponent, 
  MarkPointComponent, 
  TitleComponent
]);

// 定义属性
const props = defineProps({
  results: {
    type: Object,
    default: () => null,
  }
});

// 图表引用
const chartContainerRef = ref(null);
const chartInstance = ref(null);

// 格式化买入信号点
const formatBuySignals = (signals = []) => {
  if (!signals || !Array.isArray(signals)) return [];
  return signals.map(s => ({
    name: '买入',
    coord: [s.date, s.price],
    itemStyle: { color: '#4caf50' },
    symbol: 'arrow',
    symbolSize: 15,
    label: {
      show: true,
      position: 'top',
      formatter: '买入',
      fontSize: 12,
      color: '#4caf50'
    }
  }));
};

// 格式化卖出信号点
const formatSellSignals = (signals = []) => {
  if (!signals || !Array.isArray(signals)) return [];
  return signals.map(s => ({
    name: '卖出',
    coord: [s.date, s.price],
    itemStyle: { color: '#f44336' },
    symbol: 'arrow',
    symbolSize: 15,
    symbolRotate: 180,
    label: {
      show: true,
      position: 'bottom',
      formatter: '卖出',
      fontSize: 12,
      color: '#f44336'
    }
  }));
};

// 初始化图表
const initChart = () => {
  try {
    if (chartContainerRef.value && !chartInstance.value) {
      // 确保容器有尺寸
      const container = chartContainerRef.value;
      if (container.clientWidth === 0 || container.clientHeight === 0) {
        container.style.width = '100%';
        container.style.height = '70vh';
        console.log('调整图表容器尺寸');
      }
      
      // 再次检查尺寸
      console.log('容器尺寸：', container.clientWidth, 'x', container.clientHeight);
      
      // 初始化图表
      chartInstance.value = echarts.init(chartContainerRef.value);
      console.log('图表初始化成功');
      
      // 更新图表选项
      updateChartOptions();
      
      // 监听窗口大小变化以自适应
      window.addEventListener('resize', handleResize);
    }
  } catch (error) {
    console.error('图表初始化错误:', error);
  }
};

// 更新图表选项
const updateChartOptions = () => {
  try {
    if (!props.results || !props.results.chart_data || !chartInstance.value) {
      console.warn('无法更新图表，数据或图表实例不存在');
      return;
    }
    
    const { chart_data } = props.results;
    console.log('更新图表数据', chart_data);
    
    // 处理资产曲线数据格式
    const equityCurveData = Array.isArray(chart_data.equity_curve) 
      ? chart_data.equity_curve.map(item => [item.date, item.value]) 
      : [];
    
    // 图表选项配置 - 适应宽屏
    const option = {
      backgroundColor: '#fff',
      title: [
        { text: '价格与移动平均线', left: 'center', top: 0, textStyle: { fontSize: 16 } },
        { text: '资产净值', left: 'center', top: '70%', textStyle: { fontSize: 16 } }
      ],
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        formatter: function(params) {
          const date = params[0].axisValue;
          let htmlStr = `<div style="font-size:14px;color:#666;font-weight:400;line-height:1;">日期：${date}</div>`;
          
          params.forEach(param => {
            const color = param.color;
            const seriesName = param.seriesName;
            const value = param.value;
            
            if (seriesName === '资产净值') {
              htmlStr += `<div style="margin-top:5px;"><span style="display:inline-block;margin-right:5px;border-radius:50%;width:10px;height:10px;background-color:${color};"></span>${seriesName}：${value && value[1] ? value[1].toFixed(2) : 'N/A'}</div>`;
            } else if (value !== undefined && !isNaN(value)) {
              htmlStr += `<div style="margin-top:5px;"><span style="display:inline-block;margin-right:5px;border-radius:50%;width:10px;height:10px;background-color:${color};"></span>${seriesName}：${value.toFixed(2)}</div>`;
            }
          });
          
          return htmlStr;
        }
      },
      legend: [
        {
          data: ['收盘价', '短期MA', '长期MA'],
          top: 30,
          textStyle: { fontSize: 12 },
          itemWidth: 15,
          itemHeight: 10
        },
        {
          data: ['资产净值'],
          top: '70%',
          textStyle: { fontSize: 12 },
          itemWidth: 15,
          itemHeight: 10
        }
      ],
      axisPointer: {
        link: {xAxisIndex: 'all'},
        label: {
          backgroundColor: '#777'
        }
      },
      grid: [
        {
          left: '3%',
          right: '3%',
          top: 70,
          height: '55%',
          containLabel: true
        },
        {
          left: '3%',
          right: '3%',
          top: '75%',
          height: '20%',
          containLabel: true
        }
      ],
      xAxis: [
        {
          type: 'category',
          data: chart_data.dates || [],
          boundaryGap: false,
          axisLine: {onZero: false},
          splitLine: {show: false},
          axisLabel: {
            show: true,
            fontSize: 10,
            rotate: 45,
            formatter: function(value) {
              // 简化日期显示，提高清晰度
              return value.substring(5); // 仅显示月-日
            }
          }
        },
        {
          type: 'category',
          gridIndex: 1,
          data: chart_data.dates || [],
          boundaryGap: false,
          axisLine: {onZero: false},
          splitLine: {show: false},
          axisLabel: {
            fontSize: 10,
            rotate: 45,
            formatter: function(value) {
              return value.substring(5);
            }
          }
        }
      ],
      yAxis: [
        {
          scale: true,
          splitLine: {show: true},
          splitArea: {show: true},
          axisLabel: {
            fontSize: 10
          }
        },
        {
          gridIndex: 1,
          scale: true,
          splitNumber: 2,
          axisLabel: {
            show: true,
            fontSize: 10
          },
          axisLine: {show: true},
          axisTick: {show: true},
          splitLine: {show: true}
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 0,
          end: 100
        },
        {
          show: true,
          xAxisIndex: [0, 1],
          type: 'slider',
          bottom: 10,
          start: 0,
          end: 100,
          height: 20
        }
      ],
      series: [
        // 收盘价
        {
          name: '收盘价',
          type: 'line',
          data: chart_data.close_prices || [],
          smooth: false,
          symbol: 'none',
          lineStyle: {
            width: 2,
            color: '#5470c6'
          },
          markPoint: {
            data: [
              ...formatBuySignals(chart_data.buy_signals),
              ...formatSellSignals(chart_data.sell_signals)
            ]
          }
        },
        // 短期移动平均线
        {
          name: '短期MA',
          type: 'line',
          data: chart_data.short_ma || [],
          smooth: true,
          symbol: 'none',
          lineStyle: {
            width: 2,
            color: '#91cc75'
          }
        },
        // 长期移动平均线
        {
          name: '长期MA',
          type: 'line',
          data: chart_data.long_ma || [],
          smooth: true,
          symbol: 'none',
          lineStyle: {
            width: 2,
            color: '#ee6666'
          }
        },
        // 资产净值
        {
          name: '资产净值',
          type: 'line',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: equityCurveData,
          smooth: true,
          symbol: 'none',
          lineStyle: {
            width: 2,
            color: '#5470c6'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: 'rgba(84, 112, 198, 0.5)'
              },
              {
                offset: 1,
                color: 'rgba(84, 112, 198, 0.1)'
              }
            ])
          }
        }
      ]
    };
    
    // 设置图表选项
    chartInstance.value.setOption(option, true);
    console.log('图表选项已更新');
  } catch (error) {
    console.error('更新图表选项错误:', error);
  }
};

// 窗口大小变化处理函数
const handleResize = () => {
  if (chartInstance.value) {
    chartInstance.value.resize();
  }
};

// 组件挂载时初始化图表
onMounted(() => {
  if (props.results && props.results.chart_data) {
    console.log('组件挂载，准备初始化图表');
    // 使用 setTimeout 确保 DOM 完全渲染
    setTimeout(() => {
      initChart();
    }, 300);
  }
});

// 组件卸载前清理资源
onBeforeUnmount(() => {
  if (chartInstance.value) {
    chartInstance.value.dispose();
    chartInstance.value = null;
  }
  window.removeEventListener('resize', handleResize);
});

// 监听结果变化，更新图表
watch(() => props.results, (newResults) => {
  console.log('结果数据变化', newResults);
  if (newResults && newResults.chart_data) {
    // 使用 setTimeout 确保 DOM 完全渲染
    setTimeout(() => {
      if (!chartInstance.value && chartContainerRef.value) {
        console.log('初始化新图表');
        initChart();
      } else if (chartInstance.value) {
        console.log('更新已有图表');
        updateChartOptions();
      }
    }, 300);
  } else if (chartInstance.value) {
    chartInstance.value.clear();
  }
}, { deep: true });
</script>

<style scoped>
.chart-container {
  height: 70vh;
  width: 100%;
  min-height: 600px;
}

@media (max-width: 768px) {
  .chart-container {
    height: 50vh;
    min-height: 400px;
  }
}
</style> 