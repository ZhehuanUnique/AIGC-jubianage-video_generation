<template>
  <div class="relative min-h-screen bg-gray-50">
    <!-- 历史视频区域（全屏滚动） -->
    <div class="pb-[600px] pt-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- 日期标题 -->
        <h2 class="text-2xl font-bold text-gray-800 mb-6">今天</h2>

        <!-- 历史视频网格 -->
        <!-- 只在首次加载且没有视频时显示加载状态，避免刷新时闪烁 -->
        <div v-if="historyStore.loading && historyStore.videos.length === 0" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
          <p class="text-gray-500 mt-4">加载中...</p>
        </div>
        <div v-else-if="historyStore.videos.length === 0" class="text-center py-12">
          <p class="text-gray-500">暂无历史视频</p>
        </div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <div
            v-for="video in historyStore.videos"
            :key="video.id"
            class="group relative bg-white rounded-xl shadow-sm hover:shadow-lg transition-all"
            style="overflow: visible;"
            @mouseenter="handleVideoHover(video.id, true)"
            @mouseleave="handleVideoHover(video.id, false)"
          >
            <!-- 视频容器 -->
            <div 
              class="relative aspect-video bg-gray-100"
              :style="video.status !== 'completed' && video.first_frame_url ? getBackgroundStyle(video.first_frame_url) : {}"
            >
              <video
                :ref="el => setVideoRef(video.id, el)"
                :src="video.video_url"
                class="w-full h-full object-cover"
                muted
                loop
                preload="metadata"
              />
              <!-- 状态覆盖层 -->
              <div v-if="video.status !== 'completed'" class="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                <div class="text-center text-white px-4 w-full">
                  <div v-if="video.status === 'processing' || video.status === 'pending'" class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white mb-2"></div>
                  <p class="text-sm font-medium mb-2">{{ getStatusText(video.status) }}</p>
                  <!-- 进度条 -->
                  <div v-if="video.status === 'processing' || video.status === 'pending'" class="w-full max-w-xs mx-auto mb-2">
                    <div class="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                      <div 
                        class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        :style="{ width: `${getEstimatedProgress(video)}%` }"
                      ></div>
                    </div>
                    <p class="text-xs text-gray-300 mt-1">{{ Math.round(getEstimatedProgress(video)) }}%</p>
                  </div>
                  <p v-if="video.status === 'processing' || video.status === 'pending'" class="text-xs text-gray-300">
                    {{ getStatusHint(video) }}
                  </p>
                </div>
              </div>
              <!-- 删除按钮（右上角） -->
              <button
                @click.stop="handleDeleteVideo(video.id)"
                class="absolute top-2 right-2 w-8 h-8 rounded-full bg-red-500 bg-opacity-90 flex items-center justify-center text-white hover:bg-opacity-100 opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                title="删除视频"
              >
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
              </button>
              <!-- 操作按钮（右下角） -->
              <div class="absolute bottom-2 right-2 flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <!-- 第一行：分辨率提升和帧率提升 -->
                <div class="flex gap-2">
                  <!-- 分辨率提升按钮 -->
                  <div class="relative">
                    <button
                      @click.stop="showResolutionOptions = showResolutionOptions === video.id ? null : video.id"
                      :class="[
                        'w-8 h-8 rounded-full bg-blue-500 bg-opacity-90 flex items-center justify-center text-white hover:bg-opacity-100',
                        video.is_ultra_hd && 'bg-blue-600 bg-opacity-100'
                      ]"
                      title="提升分辨率"
                    >
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M21 3H3c-1.11 0-2 .89-2 2v14c0 1.11.89 2 2 2h18c1.11 0 2-.89 2-2V5c0-1.11-.89-2-2-2zm0 16H3V5h18v14zm-5.04-6.71l-2.75 3.54-1.96-2.36L6.5 17h11l-3.54-4.71z"/>
                      </svg>
                    </button>
                    <!-- 分辨率选项下拉菜单 -->
                    <div
                      v-if="showResolutionOptions === video.id"
                      @click.stop
                      class="absolute bottom-full right-0 mb-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 p-2 z-[100]"
                      style="max-height: 200px; overflow-y: auto;"
                    >
                      <div class="text-xs font-semibold text-gray-700 mb-2">选择超分辨率方法</div>
                      <button
                        @click="handleEnhanceResolution(video.id, 'real_esrgan')"
                        class="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                      >
                        Real-ESRGAN
                      </button>
                      <button
                        @click="handleEnhanceResolution(video.id, 'waifu2x')"
                        class="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                      >
                        Waifu2x
                      </button>
                    </div>
                  </div>
                  <!-- 帧率提升按钮 -->
                  <div class="relative">
                    <button
                      @click.stop="showFPSOptions = showFPSOptions === video.id ? null : video.id"
                      class="w-8 h-8 rounded-full bg-green-500 bg-opacity-90 flex items-center justify-center text-white hover:bg-opacity-100"
                      title="提升帧率（24fps -> 60fps）"
                    >
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                      </svg>
                    </button>
                    <!-- 帧率选项下拉菜单 -->
                    <div
                      v-if="showFPSOptions === video.id"
                      @click.stop
                      class="absolute bottom-full right-0 mb-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 p-2 z-[100]"
                      style="max-height: 200px; overflow-y: auto;"
                    >
                      <div class="text-xs font-semibold text-gray-700 mb-2">选择插帧方法</div>
                      <button
                        @click="handleEnhanceFPS(video.id, 'rife')"
                        class="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                      >
                        RIFE（快速，默认）
                      </button>
                      <button
                        @click="handleEnhanceFPS(video.id, 'film')"
                        class="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                      >
                        FILM（大运动，较慢）
                      </button>
                    </div>
                  </div>
                </div>
                <!-- 第二行：收藏和点赞 -->
                <div class="flex gap-2">
                  <!-- 收藏按钮（五角星） -->
                  <button
                    @click.stop="toggleFavorite(video.id)"
                    :class="[
                      'w-8 h-8 rounded-full bg-black bg-opacity-50 flex items-center justify-center text-white hover:bg-opacity-70',
                      video.is_favorite && 'bg-yellow-500 bg-opacity-100'
                    ]"
                    :title="video.is_favorite ? '取消收藏' : '收藏'"
                  >
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
                    </svg>
                  </button>
                  <!-- 点赞按钮（爱心） -->
                  <button
                    @click.stop="toggleLike(video.id)"
                    :class="[
                      'w-8 h-8 rounded-full bg-black bg-opacity-50 flex items-center justify-center text-white hover:bg-opacity-70',
                      video.is_liked && 'bg-red-500 bg-opacity-100'
                    ]"
                    :title="video.is_liked ? '取消点赞' : '点赞'"
                  >
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
            <!-- 视频信息 -->
            <div class="p-3">
              <p class="text-sm text-gray-700 line-clamp-2 mb-2">{{ video.prompt }}</p>
              <div class="flex items-center justify-between text-xs text-gray-500">
                <span>视频 {{ video.version || '3.0' }} | {{ video.duration }}s | {{ getResolutionText(video) }}</span>
                <span>{{ formatDate(video.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部边缘触发区域（用于检测鼠标靠近）- 始终存在，收缩时显示提示条 -->
    <div
      class="fixed bottom-0 left-0 right-0 z-50 transition-all duration-300"
      :class="isBottomBarCollapsed ? 'h-16' : 'h-4'"
      @mouseenter="handleBottomEdgeHover(true)"
      @mouseleave="handleBottomEdgeHover(false)"
      @click="isBottomBarCollapsed = false"
    >
      <!-- 收缩时显示提示条（只有小箭头，贴近底部边缘） -->
      <div v-if="isBottomBarCollapsed" class="h-full flex items-end justify-center pb-1">
        <div class="bg-white/95 backdrop-blur-sm rounded-t-lg shadow-md border-t border-x border-gray-200 px-2 py-1.5 cursor-pointer hover:bg-white transition-all hover:shadow-lg">
          <svg class="w-3 h-3 text-gray-400 hover:text-primary-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 15l7-7 7 7" />
          </svg>
        </div>
      </div>
    </div>

    <!-- 底部悬浮输入区域 -->
    <div
      :class="[
        'fixed bottom-0 left-0 right-0 z-40 transition-all duration-300 ease-in-out',
        isBottomBarCollapsed ? 'translate-y-full opacity-0 pointer-events-none' : 'translate-y-0 opacity-100'
      ]"
      @mouseenter="handleBottomBarHover(true)"
      @mouseleave="handleBottomBarHover(false)"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="bg-white rounded-t-2xl shadow-lg border-t border-x border-gray-200 p-6">
          <!-- 完整内容 -->
          <div>
          <!-- 主要内容区域：首尾帧上传（左）和提示词输入（右） -->
          <div class="flex items-start gap-6 mb-4">
            <!-- 左侧：首尾帧上传块（横向排列） -->
            <div class="flex-shrink-0 flex items-center gap-3">
              <!-- 首帧卡片 -->
              <div
                class="relative cursor-pointer group"
                @mouseenter="hoveredFrame = 'first'"
                @mouseleave="hoveredFrame = null"
                @click.stop="triggerFirstFrameUpload"
              >
                <input
                  type="file"
                  accept="image/*"
                  @change="handleFirstFrame"
                  class="hidden"
                  ref="firstFrameInput"
                />
                <div
                  :class="[
                    'relative w-24 h-24 bg-gray-50 border-2 border-dashed rounded-xl flex flex-col items-center justify-center transition-all duration-300',
                    hoveredFrame === 'first' ? 'border-primary-500 shadow-lg transform scale-105' : 'border-gray-300',
                    firstFramePreview ? 'border-primary-500 bg-white' : ''
                  ]"
                >
                  <img
                    v-if="firstFramePreview"
                    :src="firstFramePreview"
                    alt="首帧"
                    class="absolute inset-0 w-full h-full object-cover rounded-xl"
                  />
                  <div
                    v-if="!firstFramePreview"
                    class="flex flex-col items-center justify-center z-10"
                  >
                    <div class="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center mb-1">
                      <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                      </svg>
                    </div>
                    <span class="text-xs text-gray-600 font-medium">首帧</span>
                  </div>
                  <button
                    v-if="firstFramePreview"
                    @click.stop="clearFirstFrame"
                    class="absolute top-1 right-1 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center text-xs hover:bg-red-600 z-20"
                  >
                    ×
                  </button>
                </div>
              </div>

              <!-- 横向双箭头连接符（图2样式） -->
              <div class="flex items-center justify-center px-2">
                <svg class="w-5 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 12" stroke-width="1.5">
                  <!-- 左箭头 -->
                  <path d="M3 6l3-3m0 6l-3-3" stroke-linecap="round" stroke-linejoin="round" />
                  <!-- 中间线 -->
                  <path d="M6 6h12" stroke-linecap="round" />
                  <!-- 右箭头 -->
                  <path d="M18 6l3-3m0 6l-3-3" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </div>

              <!-- 尾帧卡片 -->
              <div
                class="relative cursor-pointer group"
                @mouseenter="hoveredFrame = 'last'"
                @mouseleave="hoveredFrame = null"
                @click.stop="triggerLastFrameUpload"
              >
                <input
                  type="file"
                  accept="image/*"
                  @change="handleLastFrame"
                  class="hidden"
                  ref="lastFrameInput"
                />
                <div
                  :class="[
                    'relative w-24 h-24 bg-gray-50 border-2 border-dashed rounded-xl flex flex-col items-center justify-center transition-all duration-300',
                    hoveredFrame === 'last' ? 'border-primary-500 shadow-lg transform scale-105' : 'border-gray-300',
                    lastFramePreview ? 'border-primary-500 bg-white' : ''
                  ]"
                >
                  <img
                    v-if="lastFramePreview"
                    :src="lastFramePreview"
                    alt="尾帧"
                    class="absolute inset-0 w-full h-full object-cover rounded-xl"
                  />
                  <div
                    v-if="!lastFramePreview"
                    class="flex flex-col items-center justify-center z-10"
                  >
                    <div class="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center mb-1">
                      <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                      </svg>
                    </div>
                    <span class="text-xs text-gray-600 font-medium">尾帧</span>
                  </div>
                  <button
                    v-if="lastFramePreview"
                    @click.stop="clearLastFrame"
                    class="absolute top-1 right-1 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center text-xs hover:bg-red-600 z-20"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>

            <!-- 右侧：提示词输入框 -->
            <div class="flex-1">
              <textarea
                v-model="prompt"
                placeholder="输入文字,描述你想创作的画面内容、运动方式等。例如:一个3D形象的小男孩,在公园滑滑板。"
                :class="[
                  'w-full bg-transparent border-none outline-none resize-none text-gray-700 placeholder-gray-400 transition-all min-h-[100px] text-base leading-relaxed',
                  isInputFocused ? 'ring-2 ring-primary-500 rounded-lg' : ''
                ]"
                @input="handleInput"
                @focus="handleInputFocus"
                @blur="handleInputBlur"
              />
            </div>
          </div>

          <!-- 控制栏 -->
          <div class="flex items-center justify-between pt-4 border-t border-gray-200">
            <div class="flex items-center gap-4">
              <!-- 版本选择 -->
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-600 font-medium">版本:</span>
                <button
                  v-for="ver in videoVersions"
                  :key="ver"
                  @click.stop="videoVersion = ver"
                  :class="[
                    'px-3 py-1.5 rounded-lg text-sm font-medium transition-all cursor-pointer',
                    videoVersion === ver
                      ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-sm'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
                    // 3.0 Pro 只支持 1080p 首帧，如果不符合条件则禁用
                    ver === '3.0_pro' && (resolution !== '1080p' || !firstFrame || lastFrame) && 'opacity-50 cursor-not-allowed'
                  ]"
                  :disabled="ver === '3.0_pro' && (resolution !== '1080p' || !firstFrame || lastFrame)"
                  :title="ver === '3.0_pro' && (resolution !== '1080p' || !firstFrame || lastFrame) ? '3.0 Pro 只支持 1080p 首帧（不支持尾帧）' : ''"
                >
                  {{ ver }}
                </button>
              </div>
              <!-- 分辨率选择（放在最前面，更显眼） -->
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-600 font-medium">分辨率:</span>
                <button
                  v-for="res in resolutions"
                  :key="res"
                  @click.stop="resolution = res"
                  :class="[
                    'px-3 py-1.5 rounded-lg text-sm font-medium transition-all cursor-pointer',
                    resolution === res
                      ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-sm'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  ]"
                >
                  {{ res.toUpperCase() }}
                </button>
              </div>
              <!-- 时长选择 -->
              <div class="flex items-center gap-2">
                <button
                  v-for="dur in durations"
                  :key="dur"
                  @click.stop="duration = dur"
                  :class="[
                    'px-3 py-1.5 rounded-lg text-sm font-medium transition-all cursor-pointer',
                    duration === dur
                      ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-sm'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  ]"
                >
                  {{ dur }}秒
                </button>
              </div>
            </div>
            <div class="flex items-center">
              <button
                type="button"
                @click="generateVideo"
                :disabled="!prompt.trim() || isGenerating || videoStore.isGenerating"
                :class="[
                  'px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-lg font-medium shadow-lg hover:shadow-xl hover:from-primary-600 hover:to-primary-700 active:scale-95 transition-all flex items-center gap-2',
                  (!prompt.trim() || isGenerating || videoStore.isGenerating) && 'opacity-50 cursor-not-allowed'
                ]"
              >
                <svg v-if="!isGenerating && !videoStore.isGenerating" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ (isGenerating || videoStore.isGenerating) ? '生成中...' : '生成视频' }}
              </button>
            </div>
          </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error || videoStore.error" class="fixed bottom-0 left-0 right-0 z-50 bg-red-50 border-t border-red-200 px-4 py-3">
      <div class="max-w-7xl mx-auto flex items-start gap-3">
        <svg class="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="flex-1">
          <p class="text-red-800 font-medium">请求失败</p>
          <p class="text-red-700 text-sm mt-1">{{ error || videoStore.error }}</p>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div
      v-if="showDeleteDialog"
      class="fixed inset-0 z-[9999] flex items-center justify-center bg-black bg-opacity-50"
      @click.self="cancelDeleteVideo"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">确认删除</h3>
        <p class="text-gray-700 mb-6">确定要删除这个视频吗？此操作不可恢复。</p>
        <div class="flex justify-end gap-3">
          <button
            @click="cancelDeleteVideo"
            class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            取消
          </button>
          <button
            @click="confirmDeleteVideo"
            class="px-4 py-2 text-white bg-red-500 rounded-lg hover:bg-red-600 transition-colors"
          >
            确定
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useVideoStore } from '~/stores/video'
import { useHistoryStore, type VideoHistoryItem } from '~/stores/history'

const config = useRuntimeConfig()
const videoStore = useVideoStore()
const historyStore = useHistoryStore()

// 筛选相关（从布局组件同步）
const filters = ref({
  timeRange: 'all' as 'all' | 'week' | 'month' | 'quarter' | 'custom',
  startDate: '',
  endDate: '',
  videoType: 'all' as 'all' | 'personal',
  operationType: 'all' as 'all' | 'ultra_hd' | 'favorite' | 'liked'
})

// 监听筛选更新事件
const handleFiltersUpdated = (event: CustomEvent) => {
  filters.value = { ...event.detail }
  loadHistory()
}

// 视频生成相关
const prompt = ref('')
const duration = ref(5)
const durations = [5, 10]
const resolution = ref<'720p' | '1080p'>('720p')
const resolutions: ('720p' | '1080p')[] = ['720p', '1080p']
const videoVersion = ref<'3.0' | '3.0_pro'>('3.0')
const videoVersions: ('3.0' | '3.0_pro')[] = ['3.0', '3.0_pro']
const firstFrame = ref<File | null>(null)
const lastFrame = ref<File | null>(null)
const firstFramePreview = ref<string | null>(null)
const lastFramePreview = ref<string | null>(null)
const firstFrameInput = ref<HTMLInputElement | null>(null)
const lastFrameInput = ref<HTMLInputElement | null>(null)
const isGenerating = ref(false)
const error = ref('')
const hoveredFrame = ref<'first' | 'last' | null>(null)
let historyRefreshInterval: NodeJS.Timeout | null = null

// 悬浮窗口状态 - 默认展开（显示视频生成区域）
const isBottomBarCollapsed = ref(false)
const isInputFocused = ref(false)
const isBottomEdgeHovered = ref(false)
const isBottomBarHovered = ref(false)
const showResolutionOptions = ref<number | null>(null)
const showFPSOptions = ref<number | null>(null)
const showDeleteDialog = ref(false)
const videoToDelete = ref<number | null>(null)
let scrollTimeout: NodeJS.Timeout | null = null
let bottomBarHoverTimeout: NodeJS.Timeout | null = null
let bottomEdgeHoverTimeout: NodeJS.Timeout | null = null

// 视频引用管理
const videoRefs = new Map<number, HTMLVideoElement | null>()

const setVideoRef = (videoId: number, el: HTMLVideoElement | null) => {
  if (el) {
    videoRefs.set(videoId, el)
  }
}

const handleVideoHover = (videoId: number, isHovering: boolean) => {
  const video = videoRefs.get(videoId)
  if (video) {
    if (isHovering) {
      video.play().catch(() => {})
    } else {
      video.pause()
      video.currentTime = 0
    }
  }
}

// 滚动处理
const handleScroll = () => {
  if (scrollTimeout) {
    clearTimeout(scrollTimeout)
  }
  
  scrollTimeout = setTimeout(() => {
    // 如果输入框有焦点或鼠标正在悬停，不自动收缩
    if (isInputFocused.value || isBottomBarHovered.value || isBottomEdgeHovered.value) {
      return
    }
    
    const scrollY = window.scrollY
    const windowHeight = window.innerHeight
    const documentHeight = document.documentElement.scrollHeight
    const distanceFromBottom = documentHeight - (scrollY + windowHeight)
    
    // 向上滚动时自动收缩
    // 如果不在底部附近（距离底部超过100px），则收缩
    if (distanceFromBottom > 100) {
      isBottomBarCollapsed.value = true
    }
  }, 100)
}

// 底部边缘鼠标悬停（检测鼠标靠近底部）
const handleBottomEdgeHover = (isHovering: boolean) => {
  if (bottomEdgeHoverTimeout) {
    clearTimeout(bottomEdgeHoverTimeout)
  }
  
  isBottomEdgeHovered.value = isHovering
  
  if (isHovering) {
    // 鼠标靠近底部边缘时，立即展开悬浮窗口
    isBottomBarCollapsed.value = false
  } else {
    // 延迟检查是否需要收缩
    bottomEdgeHoverTimeout = setTimeout(() => {
      // 如果输入框没有焦点且鼠标不在悬浮窗口上，则收缩
      if (!isInputFocused.value && !isBottomBarHovered.value) {
        isBottomBarCollapsed.value = true
      }
    }, 300)
  }
}

// 底部悬浮栏鼠标悬停
const handleBottomBarHover = (isHovering: boolean) => {
  if (bottomBarHoverTimeout) {
    clearTimeout(bottomBarHoverTimeout)
  }
  
  isBottomBarHovered.value = isHovering
  
  if (isHovering) {
    // 鼠标悬停在悬浮窗口上时，保持展开
    isBottomBarCollapsed.value = false
  } else {
    // 延迟检查是否需要收缩
    bottomBarHoverTimeout = setTimeout(() => {
      // 如果输入框没有焦点且鼠标不在底部边缘，则收缩
      if (!isInputFocused.value && !isBottomEdgeHovered.value) {
        isBottomBarCollapsed.value = true
      }
    }, 300)
  }
}

// 输入框焦点处理
const handleInputFocus = () => {
  isInputFocused.value = true
  isBottomBarCollapsed.value = false
}

const handleInputBlur = () => {
  isInputFocused.value = false
  // 失去焦点后，如果不在底部附近且鼠标不在悬浮区域，则收缩
  setTimeout(() => {
    if (!isBottomBarHovered.value && !isBottomEdgeHovered.value) {
      const scrollY = window.scrollY
      const windowHeight = window.innerHeight
      const documentHeight = document.documentElement.scrollHeight
      const distanceFromBottom = documentHeight - (scrollY + windowHeight)
      
      if (distanceFromBottom > 100) {
        isBottomBarCollapsed.value = true
      }
    }
  }, 200)
}

// 加载历史记录
// 防抖：避免频繁刷新
let loadHistoryTimeout: NodeJS.Timeout | null = null
let isHistoryLoading = false
const loadHistory = async (silent: boolean = false) => {
  // 如果正在加载，跳过本次请求
  if (isHistoryLoading) {
    return
  }
  
  // 防抖：如果 silent 为 false，延迟 300ms 执行
  if (!silent) {
    if (loadHistoryTimeout) {
      clearTimeout(loadHistoryTimeout)
    }
    return new Promise<void>((resolve) => {
      loadHistoryTimeout = setTimeout(async () => {
        await loadHistory(true)
        resolve()
      }, 300)
    })
  }
  
  isHistoryLoading = true
  try {
    // 只在非静默模式时输出日志
    if (!silent) {
      console.log('开始加载历史记录，后端URL:', config.public.backendUrl)
    }
    const result = await historyStore.fetchHistory({
      backendUrl: config.public.backendUrl,
      limit: 20,
      offset: 0,
      filters: filters.value,
      silent: silent // 传递静默模式参数
    })
    // 只在非静默模式或首次加载时输出日志
    if (!silent) {
      console.log('历史记录加载成功:', {
        total: result.total,
        itemsCount: result.items?.length || 0
      })
    }
  } catch (err: any) {
    // 只在非静默模式时输出错误日志
    if (!silent) {
      console.error('加载历史记录失败:', {
        error: err,
        message: err.message,
        status: err.status || err.statusCode,
        statusText: err.statusText,
        data: err.data
      })
      // 如果是404错误，可能是API路径不对或后端未部署，静默处理
      if (err.status === 404 || err.statusCode === 404) {
        console.warn('历史记录API未找到，可能是后端未部署或路径配置错误')
      } else if (err.status === 0 || err.name === 'FetchError') {
        console.warn('无法连接到后端服务，可能是后端未启动或网络问题')
      }
    }
  } finally {
    isHistoryLoading = false
  }
}

// 视频生成相关函数
const handleInput = () => {
  error.value = ''
}

const triggerFirstFrameUpload = () => {
  firstFrameInput.value?.click()
}

const triggerLastFrameUpload = () => {
  lastFrameInput.value?.click()
}

const handleFirstFrame = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    firstFrame.value = target.files[0]
    firstFramePreview.value = await fileToDataURL(target.files[0])
  }
}

const handleLastFrame = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    lastFrame.value = target.files[0]
    lastFramePreview.value = await fileToDataURL(target.files[0])
  }
}

const clearFirstFrame = () => {
  firstFrame.value = null
  firstFramePreview.value = null
  if (firstFrameInput.value) {
    firstFrameInput.value.value = ''
  }
}

const clearLastFrame = () => {
  lastFrame.value = null
  lastFramePreview.value = null
  if (lastFrameInput.value) {
    lastFrameInput.value.value = ''
  }
}

const fileToDataURL = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

const generateVideo = async () => {
  if (!prompt.value.trim()) {
    error.value = '请输入视频描述'
    return
  }

  isGenerating.value = true
  error.value = ''

  // 保存当前输入状态，以便失败时恢复
  const savedPrompt = prompt.value.trim()
  const savedFirstFrame = firstFrame.value
  const savedLastFrame = lastFrame.value
  const savedFirstFramePreview = firstFramePreview.value
  const savedLastFramePreview = lastFramePreview.value

  try {
    let firstFrameBase64 = null
    let lastFrameBase64 = null

    if (firstFrame.value) {
      console.log('正在转换首帧图片为base64...')
      firstFrameBase64 = await fileToBase64(firstFrame.value)
      console.log('首帧图片转换完成，长度:', firstFrameBase64.length)
    }
    if (lastFrame.value) {
      console.log('正在转换尾帧图片为base64...')
      lastFrameBase64 = await fileToBase64(lastFrame.value)
      console.log('尾帧图片转换完成，长度:', lastFrameBase64.length)
    }

    console.log('开始调用视频生成API...', {
      prompt: savedPrompt,
      duration: duration.value,
      hasFirstFrame: !!firstFrameBase64,
      hasLastFrame: !!lastFrameBase64,
      backendUrl: config.public.backendUrl
    })

    console.log('开始调用视频生成API...', {
      prompt: savedPrompt,
      duration: duration.value,
      hasFirstFrame: !!firstFrameBase64,
      hasLastFrame: !!lastFrameBase64,
      backendUrl: config.public.backendUrl
    })

    const result = await videoStore.generateVideo({
      prompt: savedPrompt,
      duration: duration.value,
      firstFrame: firstFrameBase64,
      lastFrame: lastFrameBase64,
      resolution: resolution.value,
      version: videoVersion.value,
      backendUrl: config.public.backendUrl
    })

    console.log('视频生成API响应:', result)

    // 如果成功提交任务，立即添加到历史记录（乐观更新）
    if (result && result.task_id) {
      console.log('视频生成任务已提交，task_id:', result.task_id)
      
      // 立即创建一个临时视频记录，添加到列表顶部
      const tempVideo: VideoHistoryItem = {
        id: -1, // 临时ID，等待后端返回真实ID
        task_id: result.task_id,
        prompt: savedPrompt,
        duration: duration.value,
        fps: 24,
        width: resolution.value === '1080p' ? 1920 : 1280,
        height: resolution.value === '1080p' ? 1080 : 720,
        status: 'pending',
        video_url: undefined,
        video_name: undefined,
        first_frame_url: savedFirstFramePreview || undefined,
        last_frame_url: savedLastFramePreview || undefined,
        created_at: new Date().toISOString(),
        completed_at: undefined,
        is_ultra_hd: false,
        is_favorite: false,
        is_liked: false,
        version: videoVersion.value // 保存版本信息
      }
      
      // 立即添加到列表顶部
      historyStore.videos.unshift(tempVideo)
      historyStore.total += 1
      
      // 成功后才清空输入
      prompt.value = ''
      firstFrame.value = null
      lastFrame.value = null
      firstFramePreview.value = null
      lastFramePreview.value = null
      
      // 立即刷新历史记录（不延迟），用真实数据替换临时记录
      // 使用 setTimeout 0 确保在下一个事件循环中执行，让UI先更新
      setTimeout(() => {
        loadHistory().catch(err => {
          console.warn('刷新历史记录失败:', err)
          // 即使失败，临时记录也会显示，用户可以继续使用
        })
      }, 0)
      
      // 清除之前的定时器（如果有）
      if (historyRefreshInterval) {
        clearInterval(historyRefreshInterval)
        historyRefreshInterval = null
      }
      
      // 定期刷新历史记录（每10秒），直到视频生成完成
      // 使用静默模式，减少日志输出
      historyRefreshInterval = setInterval(async () => {
        try {
          await loadHistory(true) // 静默模式，不输出日志
        } catch (err: any) {
          // 只在出错时输出日志
          console.warn('定期刷新历史记录失败:', err)
        }
      }, 10000) // 每10秒刷新一次（从5秒改为10秒，减少请求频率）
      
      // 6分钟后停止定期刷新（视频应该已经完成或超时）
      // 后端超时设置为5分钟，这里6分钟确保能检测到超时
      setTimeout(() => {
        if (historyRefreshInterval) {
          clearInterval(historyRefreshInterval)
          historyRefreshInterval = null
        }
      }, 360000) // 6分钟
    } else {
      throw new Error('视频生成失败：未返回task_id')
    }
  } catch (err: any) {
    console.error('生成视频失败:', err)
    console.error('错误详情:', {
      message: err.message,
      statusCode: err.statusCode,
      name: err.name,
      stack: err.stack
    })
    error.value = err.message || '生成失败，请重试'
    
    // 失败时恢复输入状态（包括图片）
    prompt.value = savedPrompt
    firstFrame.value = savedFirstFrame
    lastFrame.value = savedLastFrame
    firstFramePreview.value = savedFirstFramePreview
    lastFramePreview.value = savedLastFramePreview
    
    // 即使失败也尝试刷新历史记录（可能之前有记录）
    try {
      await loadHistory()
    } catch (historyErr: any) {
      console.warn('刷新历史记录失败:', historyErr)
    }
  } finally {
    isGenerating.value = false
  }
}

const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const result = reader.result as string
      const base64 = result.split(',')[1]
      resolve(base64)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

const toggleFavorite = async (videoId: number) => {
  // 乐观更新：立即更新UI
  const video = historyStore.videos.find(v => v.id === videoId)
  if (video) {
    const oldValue = video.is_favorite
    video.is_favorite = !oldValue
    
    // 异步更新后端，如果失败则回滚
    try {
      await historyStore.toggleFavorite(videoId, config.public.backendUrl)
    } catch (error) {
      // 回滚UI状态
      video.is_favorite = oldValue
      console.error('切换收藏状态失败:', error)
      alert('操作失败，请重试')
    }
  }
}

const toggleLike = async (videoId: number) => {
  // 乐观更新：立即更新UI
  const video = historyStore.videos.find(v => v.id === videoId)
  if (video) {
    const oldValue = video.is_liked
    video.is_liked = !oldValue
    
    // 异步更新后端，如果失败则回滚
    try {
      await historyStore.toggleLike(videoId, config.public.backendUrl)
    } catch (error) {
      // 回滚UI状态
      video.is_liked = oldValue
      console.error('切换点赞状态失败:', error)
      alert('操作失败，请重试')
    }
  }
}

const handleDeleteVideo = (videoId: number) => {
  videoToDelete.value = videoId
  showDeleteDialog.value = true
}

const confirmDeleteVideo = async () => {
  if (!videoToDelete.value) return
  
  // 乐观更新：立即从UI中移除
  const videoId = videoToDelete.value
  const video = historyStore.videos.find(v => v.id === videoId)
  const videoIndex = historyStore.videos.findIndex(v => v.id === videoId)
  
  // 先关闭对话框
  showDeleteDialog.value = false
  const tempVideoId = videoToDelete.value
  videoToDelete.value = null
  
  // 立即从列表中移除（乐观更新）
  if (videoIndex !== -1) {
    historyStore.videos.splice(videoIndex, 1)
    historyStore.total = Math.max(0, historyStore.total - 1)
  }
  
  // 异步删除后端数据，如果失败则恢复
  try {
    await historyStore.deleteVideo(tempVideoId, config.public.backendUrl)
  } catch (err: any) {
    // 恢复UI状态
    if (video && videoIndex !== -1) {
      historyStore.videos.splice(videoIndex, 0, video)
      historyStore.total += 1
    }
    console.error('删除视频失败:', err)
    alert('删除失败：' + (err.message || '未知错误'))
  }
}

const cancelDeleteVideo = () => {
  showDeleteDialog.value = false
  videoToDelete.value = null
}

const handleEnhanceResolution = async (videoId: number, method: 'real_esrgan' | 'waifu2x') => {
  showResolutionOptions.value = null
  
  if (!confirm(`确定要使用 ${method === 'real_esrgan' ? 'Real-ESRGAN' : 'Waifu2x'} 提升分辨率吗？处理可能需要几分钟。`)) {
    return
  }
  
  try {
    const result = await historyStore.enhanceResolution(videoId, config.public.backendUrl, method)
    alert(`分辨率提升成功！\n原始分辨率: ${result.original_resolution[0]}x${result.original_resolution[1]}\n提升后: ${result.enhanced_resolution[0]}x${result.enhanced_resolution[1]}\n处理时间: ${result.processing_time.toFixed(1)}秒`)
    // 刷新历史记录
    await loadHistory()
  } catch (err: any) {
    console.error('分辨率提升失败:', err)
    alert('分辨率提升失败：' + (err.message || '未知错误'))
  }
}

const handleEnhanceFPS = async (videoId: number, method: 'rife' | 'film') => {
  showFPSOptions.value = null
  
  if (method === 'film') {
    if (!confirm('使用 FILM 处理时间较长，请耐心等待。确定继续吗？')) {
      return
    }
  } else {
    if (!confirm(`确定要使用 RIFE 提升帧率到 60fps 吗？处理可能需要几分钟。`)) {
      return
    }
  }
  
  try {
    const result = await historyStore.enhanceFPS(videoId, config.public.backendUrl, method)
    let message = `帧率提升成功！\n原始帧率: ${result.original_fps}fps\n提升后: ${result.enhanced_fps}fps\n处理时间: ${result.processing_time.toFixed(1)}秒`
    if (result.auto_switched) {
      message += '\n\n已自动检测到大运动，切换到 FILM 处理'
    }
    if (result.warning) {
      message += '\n\n' + result.warning
    }
    alert(message)
    // 刷新历史记录
    await loadHistory()
  } catch (err: any) {
    console.error('帧率提升失败:', err)
    alert('帧率提升失败：' + (err.message || '未知错误'))
  }
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '等待中',
    processing: '生成中',
    completed: '已完成',
    failed: '生成失败'
  }
  return statusMap[status] || status
}

const getStatusHint = (video: any) => {
  if (video.status === 'processing' || video.status === 'pending') {
    // 计算已等待时间，添加验证
    if (!video.created_at) {
      return '正在生成中，请稍候...'
    }
    
    try {
      // 尝试解析时间，支持多种格式
      let createdTime: number
      if (typeof video.created_at === 'string') {
        // 处理 ISO 格式字符串
        // 如果字符串没有时区信息，假设是 UTC 时间
        let dateString = video.created_at
        if (!dateString.includes('Z') && !dateString.includes('+') && !dateString.includes('-', 10)) {
          // 没有时区信息，添加 Z 表示 UTC
          dateString = dateString.endsWith('Z') ? dateString : dateString + 'Z'
        }
        createdTime = new Date(dateString).getTime()
      } else if (typeof video.created_at === 'number') {
        createdTime = video.created_at
      } else {
        console.warn('无法解析创建时间类型:', typeof video.created_at, video.created_at)
        return '正在生成中，请稍候...'
      }
      
      const now = Date.now()
      
      // 验证时间是否有效
      if (isNaN(createdTime) || createdTime <= 0) {
        console.warn('无效的创建时间:', video.created_at, 'parsed:', createdTime)
        return '正在生成中，请稍候...'
      }
      
      // 如果创建时间在未来（可能是时区问题或数据错误），使用当前时间
      if (createdTime > now + 60000) { // 允许1分钟的误差
        console.warn('创建时间在未来，可能是时区问题或数据错误:', {
          created_at: video.created_at,
          createdTime,
          now,
          diff: createdTime - now,
          diffMinutes: Math.floor((createdTime - now) / 60000)
        })
        return '正在生成中，请稍候...'
      }
      
      const elapsedSeconds = Math.floor((now - createdTime) / 1000)
      const elapsedMinutes = Math.floor(elapsedSeconds / 60)
      
      // 如果计算出的时间是负数（未来时间），直接返回
      if (elapsedMinutes < 0) {
        console.warn('计算出的等待时间为负数，可能是未来时间:', {
          created_at: video.created_at,
          createdTime,
          now,
          elapsedMinutes
        })
        return '正在生成中，请稍候...'
      }
      
      // 如果时间差异常大（超过30分钟），可能是数据错误，不显示具体时间
      // 正常视频生成应该在1-3分钟内完成，超过30分钟肯定是异常
      if (elapsedMinutes > 30) {
        console.warn('时间差异常大，可能是数据错误或旧记录:', {
          created_at: video.created_at,
          elapsedMinutes,
          task_id: video.task_id
        })
        return '正在生成中，请稍候...'
      }
      
      // 如果超过10分钟，提示可能有问题
      if (elapsedMinutes > 10) {
        return `已等待 ${elapsedMinutes} 分钟，如果超过15分钟仍未完成，请刷新页面或重新生成`
      }
      
      if (elapsedMinutes < 1) {
        return '通常需要 1-3 分钟，请稍候...'
      } else if (elapsedMinutes < 3) {
        return `已等待 ${elapsedMinutes} 分钟，即将完成...`
      } else {
        return `已等待 ${elapsedMinutes} 分钟，请耐心等待...`
      }
    } catch (error) {
      console.error('计算等待时间失败:', error, 'created_at:', video.created_at, 'type:', typeof video.created_at)
      return '正在生成中，请稍候...'
    }
  }
  return ''
}

// 获取背景样式（处理base64图片格式）
const getBackgroundStyle = (firstFrameUrl: string) => {
  if (!firstFrameUrl) return {}
  
  // 如果已经是完整的 data URL，直接使用
  if (firstFrameUrl.startsWith('data:')) {
    return {
      backgroundImage: `url(${firstFrameUrl})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  
  // 如果是纯 base64 字符串，添加前缀
  // 尝试检测图片类型（默认使用 jpeg）
  let mimeType = 'image/jpeg'
  if (firstFrameUrl.startsWith('/9j/') || firstFrameUrl.startsWith('iVBORw0KGgo')) {
    // JPEG 或 PNG
    mimeType = firstFrameUrl.startsWith('/9j/') ? 'image/jpeg' : 'image/png'
  }
  
  return {
    backgroundImage: `url(data:${mimeType};base64,${firstFrameUrl})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center'
  }
}

// 估算进度百分比（基于等待时间）
const getEstimatedProgress = (video: any): number => {
  // 如果有后端返回的进度，优先使用
  if (video.progress !== undefined && video.progress !== null) {
    return Math.min(100, Math.max(0, video.progress))
  }
  
  // 否则基于等待时间估算
  if (!video.created_at) {
    return 10
  }
  
  try {
    let createdTime: number
    if (typeof video.created_at === 'string') {
      // 处理时区问题：如果没有时区信息，假设是 UTC
      let dateString = video.created_at
      if (!dateString.includes('Z') && !dateString.includes('+') && !dateString.includes('-', 10)) {
        dateString = dateString.endsWith('Z') ? dateString : dateString + 'Z'
      }
      createdTime = new Date(dateString).getTime()
    } else if (typeof video.created_at === 'number') {
      createdTime = video.created_at
    } else {
      return 10
    }
    
    const now = Date.now()
    
    if (isNaN(createdTime) || createdTime <= 0 || createdTime > now + 60000) {
      return 10
    }
    
    const elapsedSeconds = Math.floor((now - createdTime) / 1000)
    const elapsedMinutes = elapsedSeconds / 60
    
    // 如果计算出的时间是负数（未来时间），返回默认值
    if (elapsedMinutes < 0) {
      return 10
    }
    
    // 如果时间差异常大（超过30分钟），返回固定值
    // 正常视频生成应该在1-3分钟内完成
    if (elapsedMinutes > 30) {
      return 95 // 可能是旧数据或异常数据，显示95%
    }
    
    // 假设正常生成时间为 1-3 分钟
    // 1分钟内：10-40%
    // 1-2分钟：40-70%
    // 2-3分钟：70-95%
    // 超过3分钟：95%（等待完成）
    
    if (elapsedMinutes < 1) {
      return Math.min(40, 10 + (elapsedMinutes / 1) * 30)
    } else if (elapsedMinutes < 2) {
      return Math.min(70, 40 + ((elapsedMinutes - 1) / 1) * 30)
    } else if (elapsedMinutes < 3) {
      return Math.min(95, 70 + ((elapsedMinutes - 2) / 1) * 25)
    } else {
      return 95 // 超过3分钟，显示95%，等待完成
    }
  } catch (error) {
    console.error('计算进度失败:', error, 'created_at:', video.created_at)
    return 10
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

// 根据视频宽高获取分辨率文本
const getResolutionText = (video: any): string => {
  if (!video.width || !video.height) {
    return '720p' // 默认值
  }
  
  // 判断分辨率：1080p = 1920x1080, 720p = 1280x720
  if (video.width === 1920 && video.height === 1080) {
    return '1080p'
  } else if (video.width === 1280 && video.height === 720) {
    return '720p'
  } else {
    // 如果宽高不匹配标准值，根据高度判断
    if (video.height >= 1080) {
      return '1080p'
    } else {
      return '720p'
    }
  }
}

// 视频状态更新事件处理函数
const handleVideoStatusUpdated = () => {
  loadHistory().catch(err => {
    console.warn('自动刷新历史记录失败:', err)
  })
  // 视频完成后，停止定期刷新
  if (historyRefreshInterval) {
    clearInterval(historyRefreshInterval)
    historyRefreshInterval = null
  }
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative') && !target.closest('.fixed')) {
    showResolutionOptions.value = null
    showFPSOptions.value = null
  }
}

onMounted(() => {
  loadHistory()
  window.addEventListener('scroll', handleScroll, { passive: true })
  window.addEventListener('filters-updated', handleFiltersUpdated as EventListener)
  // 监听视频状态更新事件，自动刷新历史记录
  window.addEventListener('video-status-updated', handleVideoStatusUpdated)
  // 点击外部关闭下拉菜单
  document.addEventListener('click', handleClickOutside)
  
  // 初始状态：默认收缩
  // 延迟检查，确保DOM已渲染
  setTimeout(() => {
    const scrollY = window.scrollY
    const windowHeight = window.innerHeight
    const documentHeight = document.documentElement.scrollHeight
    const distanceFromBottom = documentHeight - (scrollY + windowHeight)
    
    // 如果不在底部附近（超过100px），默认收缩
    // 否则保持展开（用户可能在底部）
    if (distanceFromBottom > 100) {
      isBottomBarCollapsed.value = true
    }
  }, 200)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('filters-updated', handleFiltersUpdated as EventListener)
  if (handleVideoStatusUpdatedRef.value) {
    window.removeEventListener('video-status-updated', handleVideoStatusUpdatedRef.value)
  }
  document.removeEventListener('click', handleClickOutside)
  if (scrollTimeout) clearTimeout(scrollTimeout)
  if (bottomBarHoverTimeout) clearTimeout(bottomBarHoverTimeout)
  if (bottomEdgeHoverTimeout) clearTimeout(bottomEdgeHoverTimeout)
  if (historyRefreshInterval) {
    clearInterval(historyRefreshInterval)
    historyRefreshInterval = null
  }
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
