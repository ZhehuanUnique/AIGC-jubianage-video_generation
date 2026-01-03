<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 导航栏 -->
    <nav class="bg-white border-b border-gray-200 shadow-sm fixed top-0 left-0 right-0 z-30">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo/标题和导航项 -->
          <div class="flex items-center gap-6">
            <div class="flex items-center gap-3">
              <img src="/logo.png" alt="Logo" class="h-8 w-8 object-contain" />
              <h1 class="text-xl font-bold text-gray-800">
                剧变时代
              </h1>
            </div>
            
            <!-- 导航项 -->
            <div class="flex items-center space-x-1">
              <NuxtLink
                to="/"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                :class="isActive('/') ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-100'"
              >
                视频生成
              </NuxtLink>
              <NuxtLink
                to="/assets"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                :class="isActive('/assets') ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-100'"
              >
                资产管理
              </NuxtLink>
              <NuxtLink
                to="/knowledge"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                :class="isActive('/knowledge') ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-100'"
              >
                知识库
              </NuxtLink>
            </div>
          </div>

          <!-- 筛选选项（移到导航栏右侧） -->
          <div class="flex items-center gap-2">
            <!-- 时间筛选 -->
            <div class="relative">
              <button
                @click.stop="showTimeFilter = !showTimeFilter"
                :class="[
                  'px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2',
                  filters.timeRange !== 'all' ? 'bg-primary-50 text-primary-600' : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                ]"
              >
                时间
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="showTimeFilter ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'" />
                </svg>
              </button>
              <!-- 时间筛选下拉 -->
              <div
                v-if="showTimeFilter"
                class="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50 p-4"
                @click.stop
              >
                <div class="mb-4 flex items-center gap-2">
                  <input
                    v-model="filters.startDate"
                    type="date"
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    placeholder="开始日期"
                  />
                  <span class="text-gray-400">-</span>
                  <input
                    v-model="filters.endDate"
                    type="date"
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    placeholder="结束日期"
                  />
                </div>
                <div class="space-y-2">
                  <button
                    v-for="option in timeOptions"
                    :key="option.value"
                    @click="selectTimeRange(option.value)"
                    :class="[
                      'w-full text-left px-3 py-2 rounded-lg text-sm transition-all flex items-center justify-between',
                      filters.timeRange === option.value ? 'bg-primary-50 text-primary-600' : 'hover:bg-gray-50'
                    ]"
                  >
                    {{ option.label }}
                    <svg v-if="filters.timeRange === option.value" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- 视频类型筛选 -->
            <div class="relative">
              <button
                @click.stop="showVideoFilter = !showVideoFilter"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 bg-gray-50 text-gray-700 hover:bg-gray-100"
              >
                视频
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <div
                v-if="showVideoFilter"
                class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50 p-2"
                @click.stop
              >
                <button
                  v-for="option in videoTypeOptions"
                  :key="option.value"
                  @click="selectVideoType(option.value)"
                  :class="[
                    'w-full text-left px-3 py-2 rounded-lg text-sm transition-all flex items-center justify-between',
                    filters.videoType === option.value ? 'bg-primary-50 text-primary-600' : 'hover:bg-gray-50'
                  ]"
                >
                  {{ option.label }}
                  <svg v-if="filters.videoType === option.value" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- 操作类型筛选 -->
            <div class="relative">
              <button
                @click.stop="showOperationFilter = !showOperationFilter"
                class="px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 bg-gray-50 text-gray-700 hover:bg-gray-100"
              >
                操作类型
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <div
                v-if="showOperationFilter"
                class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50 p-2"
                @click.stop
              >
                <button
                  v-for="option in operationTypeOptions"
                  :key="option.value"
                  @click="selectOperationType(option.value)"
                  :class="[
                    'w-full text-left px-3 py-2 rounded-lg text-sm transition-all flex items-center justify-between',
                    filters.operationType === option.value ? 'bg-primary-50 text-primary-600' : 'hover:bg-gray-50'
                  ]"
                >
                  {{ option.label }}
                  <svg v-if="filters.operationType === option.value" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>


    <!-- 主内容区域 -->
    <main class="pt-16">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, provide } from 'vue'

const route = useRoute()

// 筛选相关（从子组件传递或使用provide/inject）
const showTimeFilter = ref(false)
const showVideoFilter = ref(false)
const showOperationFilter = ref(false)
const filters = ref({
  timeRange: 'all' as 'all' | 'week' | 'month' | 'quarter' | 'custom',
  startDate: '',
  endDate: '',
  videoType: 'all' as 'all' | 'group' | 'personal',
  operationType: 'all' as 'all' | 'ultra_hd' | 'favorite' | 'liked'
})

const timeOptions = [
  { label: '全部', value: 'all' },
  { label: '最近一周', value: 'week' },
  { label: '最近一个月', value: 'month' },
  { label: '最近三个月', value: 'quarter' }
]

const videoTypeOptions = [
  { label: '全部', value: 'all' },
  { label: '小组', value: 'group' },
  { label: '个人', value: 'personal' }
]

const operationTypeOptions = [
  { label: '全部', value: 'all' },
  { label: '已超清', value: 'ultra_hd' },
  { label: '已收藏', value: 'favorite' },
  { label: '已点赞', value: 'liked' }
]

const isActive = (path: string) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

const selectTimeRange = (value: string) => {
  filters.value.timeRange = value as any
  showTimeFilter.value = false
  window.dispatchEvent(new CustomEvent('filters-updated', { detail: filters.value }))
}

const selectVideoType = (value: string) => {
  filters.value.videoType = value as any
  showVideoFilter.value = false
  window.dispatchEvent(new CustomEvent('filters-updated', { detail: filters.value }))
}

const selectOperationType = (value: string) => {
  filters.value.operationType = value as any
  showOperationFilter.value = false
  window.dispatchEvent(new CustomEvent('filters-updated', { detail: filters.value }))
}

// 点击外部关闭筛选下拉
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showTimeFilter.value = false
    showVideoFilter.value = false
    showOperationFilter.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 提供筛选功能给子组件
provide('filters', filters)
provide('applyFilters', () => {
  // 触发筛选更新事件
  window.dispatchEvent(new CustomEvent('filters-updated', { detail: filters.value }))
})
</script>
