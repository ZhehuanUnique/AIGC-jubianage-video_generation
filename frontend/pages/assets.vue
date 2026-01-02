<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-800">资产管理</h2>
      <p class="text-gray-600 mt-1">上传和管理视频生成所需的图片资产</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 左侧：上传资产 -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="text-lg font-semibold mb-4">上传资产</h3>

        <!-- 文件名格式要求 -->
        <div class="mb-6 p-4 bg-blue-50 rounded-lg">
          <h4 class="text-sm font-medium text-blue-900 mb-2">文件名格式要求</h4>
          <ul class="text-sm text-blue-800 space-y-1">
            <li>格式: <code class="bg-blue-100 px-1 rounded">人物名-视图类型.扩展名</code></li>
            <li>示例: <code class="bg-blue-100 px-1 rounded">小明-正视图.jpg</code>、<code class="bg-blue-100 px-1 rounded">小美-侧视图.png</code></li>
            <li>支持格式: JPG, PNG, GIF, WebP</li>
          </ul>
        </div>

        <!-- 文件上传区域 -->
        <div
          @drop.prevent="handleDrop"
          @dragover.prevent="dragover = true"
          @dragleave.prevent="dragover = false"
          :class="[
            'border-2 border-dashed rounded-lg p-8 text-center transition-all cursor-pointer',
            dragover ? 'border-primary-500 bg-primary-50' : 'border-gray-300 bg-gray-50 hover:border-gray-400'
          ]"
          @click="triggerFileInput"
        >
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            multiple
            @change="handleFileSelect"
            class="hidden"
          />
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p class="mt-2 text-sm text-gray-600">拖拽文件到此处或点击上传</p>
          <p class="text-xs text-gray-500 mt-1">限制 200MB 每个文件 • JPG, JPEG, PNG, GIF, WEBP</p>
          <button class="mt-4 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors">
            浏览文件
          </button>
        </div>

        <!-- 已选文件列表 -->
        <div v-if="selectedFiles.length > 0" class="mt-4 space-y-2">
          <div
            v-for="(file, index) in selectedFiles"
            :key="index"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <img
                v-if="file.preview"
                :src="file.preview"
                alt="预览"
                class="w-12 h-12 object-cover rounded"
              />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ file.name }}</p>
                <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
              </div>
            </div>
            <button
              @click="removeFile(index)"
              class="ml-2 text-red-500 hover:text-red-700"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 上传按钮 -->
        <button
          v-if="selectedFiles.length > 0"
          @click="uploadAssets"
          :disabled="isUploading"
          class="mt-4 w-full px-4 py-3 bg-primary-500 text-white rounded-lg font-medium hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          <svg v-if="!isUploading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isUploading ? '上传中...' : '上传资产' }}
        </button>
      </div>

      <!-- 右侧：资产预览 -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="text-lg font-semibold mb-4">资产预览</h3>

        <!-- 错误提示 -->
        <div v-if="error" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-start gap-3">
            <svg class="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p class="text-red-800 font-medium">无法连接到后端服务</p>
              <p class="text-red-700 text-sm mt-1">{{ error }}</p>
              <p class="text-blue-600 text-sm mt-2">请确保后端服务正在运行</p>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="isLoading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mb-4"></div>
          <p class="text-gray-500">加载资产中...</p>
        </div>

        <!-- 资产列表 -->
        <div v-else-if="assets.length > 0" class="grid grid-cols-2 gap-4">
          <div
            v-for="asset in assets"
            :key="asset.filename"
            class="relative group"
          >
            <img
              :src="getAssetUrl(asset.filename)"
              :alt="asset.filename"
              class="w-full h-32 object-cover rounded-lg"
            />
            <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100">
              <button
                @click="deleteAsset(asset.filename)"
                class="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
              >
                删除
              </button>
            </div>
            <p class="mt-2 text-xs text-gray-600 truncate">{{ asset.filename }}</p>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="text-center py-12 text-gray-500">
          <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p>暂无资产</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const config = useRuntimeConfig()

interface Asset {
  filename: string
  character?: string
  view_type?: string
}

const fileInput = ref<HTMLInputElement | null>(null)
const dragover = ref(false)
const selectedFiles = ref<Array<{ file: File; preview: string; name: string; size: number }>>([])
const assets = ref<Asset[]>([])
const isLoading = ref(false)
const isUploading = ref(false)
const error = ref<string | null>(null)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    processFiles(Array.from(target.files))
  }
}

const handleDrop = (event: DragEvent) => {
  dragover.value = false
  if (event.dataTransfer?.files) {
    processFiles(Array.from(event.dataTransfer.files))
  }
}

const processFiles = async (files: File[]) => {
  for (const file of files) {
    if (file.type.startsWith('image/')) {
      const preview = await fileToDataURL(file)
      selectedFiles.value.push({
        file,
        preview,
        name: file.name,
        size: file.size
      })
    }
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

const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const uploadAssets = async () => {
  if (selectedFiles.value.length === 0) return

  isUploading.value = true
  error.value = null

  try {
    for (const item of selectedFiles.value) {
      const formData = new FormData()
      formData.append('file', item.file)

      await $fetch(`${config.public.backendUrl}/api/v1/assets/upload`, {
        method: 'POST',
        body: formData
      })
    }

    // 上传成功，清空选择列表并刷新资产列表
    selectedFiles.value = []
    await loadAssets()
  } catch (err: any) {
    error.value = err.message || '上传失败，请重试'
  } finally {
    isUploading.value = false
  }
}

const loadAssets = async () => {
  isLoading.value = true
  error.value = null

  try {
    // 后端 API 返回格式：{ "character_name": [assets...] }
    const response = await $fetch<Record<string, Asset[]>>(`${config.public.backendUrl}/api/v1/assets/list`)
    
    // 将所有角色的资产合并到一个数组
    const allAssets: Asset[] = []
    for (const characterAssets of Object.values(response)) {
      allAssets.push(...characterAssets)
    }
    
    assets.value = allAssets
  } catch (err: any) {
    error.value = err.message || '无法连接到后端服务'
    assets.value = []
  } finally {
    isLoading.value = false
  }
}

const getAssetUrl = (filename: string): string => {
  return `${config.public.backendUrl}/api/v1/assets/${filename}`
}

const deleteAsset = async (filename: string) => {
  if (!confirm(`确定要删除 ${filename} 吗？`)) return

  try {
    await $fetch(`${config.public.backendUrl}/api/v1/assets/${filename}`, {
      method: 'DELETE'
    })
    await loadAssets()
  } catch (err: any) {
    error.value = err.message || '删除失败'
  }
}

onMounted(() => {
  loadAssets()
})
</script>

