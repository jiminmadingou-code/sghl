<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  type: { type: String, default: 'bar', validator: v => ['bar', 'line', 'pie', 'donut', 'area'].includes(v) },
  data: { type: Array, default: () => [] },
  labels: { type: Array, default: () => [] },
  colors: { type: Array, default: () => ['#7c3aed', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899'] },
  title: { type: String, default: '' },
  height: { type: Number, default: 280 },
  showLegend: { type: Boolean, default: true },
  animated: { type: Boolean, default: true },
  showTooltip: { type: Boolean, default: true },
})

const svgRef = ref(null)
const animationProgress = ref(0)
let animationFrame = null
const hoveredIndex = ref(-1)
const tooltip = ref({ x: 0, y: 0, label: '', value: '' })

const maxValue = computed(() => Math.max(...props.data.map(d => typeof d === 'object' ? d.value : d), 1))
const minValue = computed(() => Math.min(...props.data.map(d => typeof d === 'object' ? d.value : d), 0))

const barWidth = computed(() => {
  const padding = 70
  const availableWidth = 600 - padding
  const barGap = 12
  const totalBars = props.data.length
  return Math.max(24, (availableWidth - barGap * (totalBars - 1)) / totalBars)
})

const chartWidth = computed(() => 600)
const chartHeight = computed(() => props.height)
const chartPadding = 70

function animateChart() {
  const duration = 1000
  const start = performance.now()
  
  function step(timestamp) {
    const elapsed = timestamp - start
    const progress = Math.min(elapsed / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 4)
    animationProgress.value = eased
    
    if (progress < 1) {
      animationFrame = requestAnimationFrame(step)
    }
  }
  
  animationFrame = requestAnimationFrame(step)
}

function handleMouseEnter(index, event, value, label) {
  if (!props.showTooltip) return
  hoveredIndex.value = index
  const rect = event.currentTarget.getBoundingClientRect()
  tooltip.value = {
    x: rect.left + rect.width / 2,
    y: rect.top - 10,
    label: label,
    value: typeof value === 'number' ? value.toLocaleString('fr-FR') : value
  }
}

function handleMouseLeave() {
  hoveredIndex.value = -1
}

onMounted(() => {
  if (props.animated) animateChart()
})

onUnmounted(() => {
  if (animationFrame) cancelAnimationFrame(animationFrame)
})

function generateBars() {
  const bars = []
  const totalWidth = barWidth.value * props.data.length + 12 * (props.data.length - 1)
  const startX = (chartWidth.value - totalWidth) / 2
  
  props.data.forEach((item, i) => {
    const value = typeof item === 'object' ? item.value : item
    const barHeight = (value / maxValue.value) * (chartHeight.value - chartPadding * 2) * animationProgress.value
    const x = startX + i * (barWidth.value + 12)
    const y = chartHeight.value - chartPadding - barHeight
    const color = props.colors[i % props.colors.length]
    const isHovered = hoveredIndex.value === i
    
    bars.push({ x, y, width: barWidth.value, height: barHeight, color, label: props.labels[i], value, isHovered })
  })
  
  return bars
}

function generateLine() {
  const points = []
  const totalWidth = chartWidth.value - chartPadding * 2
  const stepX = totalWidth / (props.data.length - 1 || 1)
  
  props.data.forEach((item, i) => {
    const value = typeof item === 'object' ? item.value : item
    const x = chartPadding + i * stepX
    const y = chartHeight.value - chartPadding - (value / maxValue.value) * (chartHeight.value - chartPadding * 2) * animationProgress.value
    points.push({ x, y, value, label: props.labels[i] })
  })
  
  if (points.length < 2) return ''
  
  const pathD = points.reduce((acc, p, i) => {
    return acc + (i === 0 ? `M ${p.x} ${p.y}` : ` L ${p.x} ${p.y}`)
  }, '')
  
  return pathD
}

function generateArea() {
  const linePath = generateLine()
  if (!linePath) return ''
  
  const lastPoint = props.data.length > 0 
    ? (chartPadding + (props.data.length - 1) * ((chartWidth.value - chartPadding * 2) / (props.data.length - 1 || 1))) 
    : chartPadding
  
  return linePath + ` L ${lastPoint} ${chartHeight.value - chartPadding} L ${chartPadding} ${chartHeight.value - chartPadding} Z`
}

function generatePie() {
  const cx = chartWidth.value / 2
  const cy = chartHeight.value / 2
  const radius = Math.min(cx, cy) - 50
  let currentAngle = -Math.PI / 2
  
  const slices = []
  const total = props.data.reduce((sum, item) => sum + (typeof item === 'object' ? item.value : item), 0)
  
  props.data.forEach((item, i) => {
    const value = typeof item === 'object' ? item.value : item
    const angle = (value / total) * 2 * Math.PI * animationProgress.value
    const color = props.colors[i % props.colors.length]
    const isHovered = hoveredIndex.value === i
    const expand = isHovered ? 8 : 0
    
    const x1 = cx + (radius + expand) * Math.cos(currentAngle)
    const y1 = cy + (radius + expand) * Math.sin(currentAngle)
    const x2 = cx + (radius + expand) * Math.cos(currentAngle + angle)
    const y2 = cy + (radius + expand) * Math.sin(currentAngle + angle)
    
    const largeArc = angle > Math.PI ? 1 : 0
    const pathD = `M ${cx} ${cy} L ${x1} ${y1} A ${radius + expand} ${radius + expand} 0 ${largeArc} 1 ${x2} ${y2} Z`
    
    slices.push({ pathD, color, label: props.labels[i], value, percentage: ((value / total) * 100).toFixed(1), isHovered })
    currentAngle += angle
  })
  
  return slices
}
</script>

<template>
  <div class="bg-white rounded-3xl border border-gray-100 p-6 shadow-lg hover:shadow-xl transition-shadow duration-300">
    <div v-if="title" class="text-base font-bold text-gray-900 mb-5 flex items-center gap-2">
      <div class="w-1 h-5 bg-gradient-to-b from-violet-500 to-purple-600 rounded-full"></div>
      {{ title }}
    </div>
    
    <svg ref="svgRef" :width="chartWidth" :height="chartHeight" class="mx-auto" viewBox="0 0 600 280">
      <!-- Grille améliorée -->
      <g v-if="type !== 'pie' && type !== 'donut'" class="grid-lines">
        <line v-for="i in 5" :key="i"
          :x1="chartPadding" :y1="chartHeight - chartPadding - ((i - 1) / 4) * (chartHeight - chartPadding * 2)"
          :x2="chartWidth - chartPadding" :stroke="'#f1f5f9'" stroke-width="1" stroke-dasharray="4,4" />
      </g>
      
      <!-- Barres -->
      <template v-if="type === 'bar'">
        <g v-for="(bar, i) in generateBars()" :key="bar.label">
          <rect :x="bar.x" :y="bar.y" :width="bar.width" :height="bar.height"
            :fill="bar.color" rx="6"
            class="transition-all duration-200 cursor-pointer"
            :class="[bar.isHovered ? 'opacity-90' : 'opacity-85']"
            :style="bar.isHovered ? `filter: drop-shadow(0 4px 8px ${bar.color}40);` : ''"
            @mouseenter="handleMouseEnter(i, $event, bar.value, bar.label)"
            @mouseleave="handleMouseLeave" />
          <text :x="bar.x + bar.width / 2" :y="chartHeight - chartPadding + 20"
            text-anchor="middle" font-size="11" font-weight="500" fill="#64748b">{{ bar.label }}</text>
          <text :x="bar.x + bar.width / 2" :y="bar.y - 8"
            text-anchor="middle" font-size="12" font-weight="700" :fill="bar.isHovered ? bar.color : '#1e293b'">{{ bar.value }}</text>
        </g>
      </template>
      
      <!-- Ligne -->
      <template v-if="type === 'line' || type === 'area'">
        <path v-if="type === 'area'" :d="generateArea()" fill="url(#areaGradient)" opacity="0.25" />
        <defs>
          <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#7c3aed" stop-opacity="0.5" />
            <stop offset="100%" stop-color="#7c3aed" stop-opacity="0.02" />
          </linearGradient>
        </defs>
        <path :d="generateLine()" fill="none" stroke="#7c3aed" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
        <circle v-for="(p, i) in (function() {
          const pts = []
          const totalWidth = chartWidth.value - chartPadding * 2
          const stepX = totalWidth / (props.data.length - 1 || 1)
          props.data.forEach((item, idx) => {
            const value = typeof item === 'object' ? item.value : item
            const x = chartPadding + idx * stepX
            const y = chartHeight.value - chartPadding - (value / maxValue) * (chartHeight.value - chartPadding * 2) * animationProgress.value
            pts.push({ x, y, value: item, label: labels[idx] })
          })
          return pts
        })()" :key="i"
          :cx="p.x" :cy="p.y" r="5" fill="white" stroke="#7c3aed" stroke-width="2.5"
          class="cursor-pointer transition-all duration-200"
          :class="[hoveredIndex === i ? 'r-7' : '']"
          :style="hoveredIndex === i ? `filter: drop-shadow(0 2px 6px #7c3aed40);` : ''"
          @mouseenter="handleMouseEnter(i, $event, p.value, p.label)"
          @mouseleave="handleMouseLeave" />
      </template>
      
      <!-- Pie / Donut -->
      <template v-if="type === 'pie' || type === 'donut'">
        <g v-for="(slice, i) in generatePie()" :key="slice.label">
          <path :d="slice.pathD" :fill="slice.color"
            class="transition-all duration-200 cursor-pointer"
            :class="[slice.isHovered ? 'opacity-90' : 'opacity-85']"
            :style="slice.isHovered ? `filter: drop-shadow(0 4px 12px ${slice.color}50);` : ''"
            @mouseenter="handleMouseEnter(i, $event, slice.value, slice.label)"
            @mouseleave="handleMouseLeave" />
          <text v-if="parseFloat(slice.percentage) > 8"
            :x="chartWidth / 2" :y="chartHeight / 2"
            text-anchor="middle" dominant-baseline="middle"
            font-size="13" font-weight="700" fill="white">
            {{ slice.percentage }}%
          </text>
        </g>
        <circle v-if="type === 'donut'" :cx="chartWidth / 2" :cy="chartHeight / 2" r="45" fill="white" />
      </template>
      
      <!-- Axes -->
      <g v-if="type !== 'pie' && type !== 'donut'" class="axes">
        <line :x1="chartPadding" :y1="chartHeight - chartPadding"
          :x2="chartWidth - chartPadding" :stroke="'#e2e8f0'" stroke-width="2" />
      </g>
    </svg>
    
    <!-- Tooltip -->
    <Teleport to="body">
      <div v-if="showTooltip && hoveredIndex >= 0"
        class="fixed z-50 pointer-events-none bg-gray-900 text-white text-xs font-semibold px-3 py-2 rounded-xl shadow-2xl border border-gray-700"
        :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px', transform: 'translate(-50%, -100%)' }">
        <p class="text-gray-300 text-[10px] mb-0.5">{{ tooltip.label }}</p>
        <p class="text-sm font-bold">{{ tooltip.value }}</p>
      </div>
    </Teleport>
    
    <!-- Légende -->
    <div v-if="showLegend && (type === 'pie' || type === 'donut')" class="flex flex-wrap justify-center gap-4 mt-5">
      <div v-for="(slice, i) in generatePie()" :key="i" class="flex items-center gap-2 text-sm">
        <div :style="{ backgroundColor: slice.color }" class="w-3 h-3 rounded-full shadow-sm"></div>
        <span class="text-gray-700 font-medium">{{ slice.label }}</span>
        <span class="text-gray-500 font-semibold">({{ slice.percentage }}%)</span>
      </div>
    </div>
  </div>
</template>
