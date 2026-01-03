import { defineStore } from 'pinia'

export interface VideoHistoryItem {
  id: number
  task_id: string
  prompt: string
  duration: number
  fps: number
  width: number
  height: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  video_url?: string
  video_name?: string
  first_frame_url?: string
  last_frame_url?: string
  created_at: string
  completed_at?: string
  is_ultra_hd?: boolean
  is_favorite?: boolean
  is_liked?: boolean
  progress?: number // 进度百分比 (0-100)
  version?: string // 版本信息：3.0pro 或 3.5pro
}

export interface VideoHistoryResponse {
  total: number
  items: VideoHistoryItem[]
  limit: number
  offset: number
}

export interface HistoryFilters {
  timeRange?: 'all' | 'week' | 'month' | 'quarter' | 'custom'
  startDate?: string
  endDate?: string
  videoType?: 'all' | 'group' | 'personal'
  operationType?: 'all' | 'ultra_hd' | 'fps_enhanced' | 'favorite' | 'liked'
  status?: 'pending' | 'processing' | 'completed' | 'failed'
}

export const useHistoryStore = defineStore('history', {
  state: () => ({
    videos: [] as VideoHistoryItem[],
    total: 0,
    loading: false,
    error: null as string | null,
    isInitialLoad: true, // 标记是否为首次加载
    filters: {
      timeRange: 'all' as const,
      videoType: 'all' as const,
      operationType: 'all' as const
    } as HistoryFilters
  }),

  actions: {
    async fetchHistory(params: {
      backendUrl: string
      limit?: number
      offset?: number
      filters?: HistoryFilters
      silent?: boolean // 静默模式，不显示加载状态
    }) {
      // 只在首次加载或非静默模式时显示加载状态
      if (this.isInitialLoad || !params.silent) {
        this.loading = true
      }
      this.error = null

      try {
        const queryParams: Record<string, string> = {
          limit: String(params.limit || 20),
          offset: String(params.offset || 0)
        }

        // 添加筛选参数
        if (params.filters?.status) {
          queryParams.status = params.filters.status
        }

        const queryString = new URLSearchParams(queryParams).toString()
        const response = await $fetch<VideoHistoryResponse>(
          `${params.backendUrl}/api/v1/video/history?${queryString}`
        )

        // 减少日志输出，只在开发环境或首次加载时输出
        // console.log('历史记录API响应:', {
        //   total: response.total,
        //   itemsCount: response.items?.length || 0,
        //   items: response.items
        // })

        // 保留临时记录（id < 0），这些是新生成但还未从后端返回的记录
        const tempVideos = this.videos.filter(v => v.id < 0)
        
        // 合并临时记录和真实记录，临时记录在前
        const allVideos = [...tempVideos, ...(response.items || [])]
        
        // 去重：如果有相同 task_id 的记录，保留真实记录（id >= 0）
        const uniqueVideos = allVideos.reduce((acc, video) => {
          const existing = acc.find(v => v.task_id === video.task_id)
          if (!existing) {
            acc.push(video)
          } else if (video.id >= 0 && existing.id < 0) {
            // 用真实记录替换临时记录
            const index = acc.indexOf(existing)
            acc[index] = video
          }
          return acc
        }, [] as VideoHistoryItem[])

        this.videos = uniqueVideos
        this.total = response.total || 0

        // 应用前端筛选（时间范围、视频类型、操作类型）
        this.applyFilters(params.filters || {})

        // 首次加载完成后，标记为非首次加载
        if (this.isInitialLoad) {
          this.isInitialLoad = false
        }

        return response
      } catch (error: any) {
        console.error('获取历史记录失败:', error)
        this.error = error.message || '获取历史记录失败'
        // 即使失败也设置空数组，显示"暂无历史记录"而不是错误
        this.videos = []
        this.total = 0
        // 首次加载失败后，也标记为非首次加载，避免一直显示加载状态
        if (this.isInitialLoad) {
          this.isInitialLoad = false
        }
        // 不抛出错误，让前端正常显示"暂无历史记录"
        // throw error
      } finally {
        // 确保加载状态被清除
        this.loading = false
      }
    },

    applyFilters(filters: HistoryFilters) {
      let filtered = [...this.videos]

      // 时间范围筛选
      if (filters.timeRange && filters.timeRange !== 'all') {
        const now = new Date()
        let cutoffDate: Date

        switch (filters.timeRange) {
          case 'week':
            cutoffDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
            break
          case 'month':
            cutoffDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
            break
          case 'quarter':
            cutoffDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
            break
          default:
            cutoffDate = new Date(0)
        }

        filtered = filtered.filter(video => {
          const videoDate = new Date(video.created_at)
          return videoDate >= cutoffDate
        })
      }

      // 自定义日期范围
      if (filters.startDate && filters.endDate) {
        const start = new Date(filters.startDate)
        const end = new Date(filters.endDate)
        filtered = filtered.filter(video => {
          const videoDate = new Date(video.created_at)
          return videoDate >= start && videoDate <= end
        })
      }

      // 操作类型筛选
      if (filters.operationType && filters.operationType !== 'all') {
        switch (filters.operationType) {
          case 'ultra_hd':
            // 只展示使用了超分辨率技术的视频
            filtered = filtered.filter(v => v.is_ultra_hd === true)
            break
          case 'fps_enhanced':
            // 只展示使用了补帧技术的视频（超帧率，24->60）
            filtered = filtered.filter(v => v.fps > 24)
            break
          case 'favorite':
            filtered = filtered.filter(v => v.is_favorite === true)
            break
          case 'liked':
            filtered = filtered.filter(v => v.is_liked === true)
            break
        }
      }

      // 视频类型筛选（全部/个人）- 目前所有视频都是个人的
      // 未来可以扩展为区分个人和共享视频

      this.videos = filtered
    },

    setFilters(filters: Partial<HistoryFilters>) {
      this.filters = { ...this.filters, ...filters }
    },

    async toggleFavorite(videoId: number, backendUrl: string) {
      try {
        const response = await $fetch<{ success: boolean; is_favorite: boolean }>(
          `${backendUrl}/api/v1/video/history/${videoId}/favorite`,
          { method: 'PATCH' }
        )
        // 不在这里更新UI，由组件进行乐观更新
        // 只返回响应，让组件处理UI更新和错误回滚
        return response
      } catch (error: any) {
        console.error('切换收藏状态失败:', error)
        throw error
      }
    },

    async toggleLike(videoId: number, backendUrl: string) {
      try {
        const response = await $fetch<{ success: boolean; is_liked: boolean }>(
          `${backendUrl}/api/v1/video/history/${videoId}/like`,
          { method: 'PATCH' }
        )
        // 不在这里更新UI，由组件进行乐观更新
        // 只返回响应，让组件处理UI更新和错误回滚
        return response
      } catch (error: any) {
        console.error('切换点赞状态失败:', error)
        throw error
      }
    },

    async deleteVideo(videoId: number, backendUrl: string) {
      try {
        const response = await $fetch<{ success: boolean; message: string }>(
          `${backendUrl}/api/v1/video/history/${videoId}`,
          { method: 'DELETE' }
        )
        // 从列表中移除已删除的视频
        this.videos = this.videos.filter(v => v.id !== videoId)
        this.total = Math.max(0, this.total - 1)
        return response
      } catch (error: any) {
        console.error('删除视频失败:', error)
        throw error
      }
    },

    async enhanceResolution(videoId: number, backendUrl: string, method: 'real_esrgan' | 'waifu2x') {
      try {
        const response = await $fetch<{
          success: boolean
          message: string
          output_url: string
          original_resolution: [number, number]
          enhanced_resolution: [number, number]
          method: string
          processing_time: number
        }>(
          `${backendUrl}/api/v1/video/history/${videoId}/enhance-resolution`,
          {
            method: 'POST',
            body: {
              method: method,
              scale: 2
            }
          }
        )
        // 更新视频信息
        const video = this.videos.find(v => v.id === videoId)
        if (video) {
          video.video_url = response.output_url
          video.width = response.enhanced_resolution[0]
          video.height = response.enhanced_resolution[1]
        }
        return response
      } catch (error: any) {
        console.error('分辨率提升失败:', error)
        throw error
      }
    },

    async enhanceFPS(videoId: number, backendUrl: string, method: 'rife' | 'film') {
      try {
        const response = await $fetch<{
          success: boolean
          message: string
          output_url: string
          original_fps: number
          enhanced_fps: number
          method: string
          auto_switched: boolean
          processing_time: number
          warning?: string
        }>(
          `${backendUrl}/api/v1/video/history/${videoId}/enhance-fps`,
          {
            method: 'POST',
            body: {
              target_fps: 60,
              method: method,
              auto_switch: true
            }
          }
        )
        // 更新视频信息
        const video = this.videos.find(v => v.id === videoId)
        if (video) {
          video.video_url = response.output_url
          video.fps = response.enhanced_fps
        }
        return response
      } catch (error: any) {
        console.error('帧率提升失败:', error)
        throw error
      }
    }
  }
})

