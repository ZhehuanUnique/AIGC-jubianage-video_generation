import { defineStore } from 'pinia'

interface VideoGenerationRequest {
  prompt: string
  duration: number
  fps?: number
  width?: number
  height?: number
  first_frame?: string | null
  last_frame?: string | null
  seed?: number | null
  resolution?: '720p' | '1080p'
  version?: '3.0' | '3.0_pro' // 版本选择
}

interface VideoGenerationResponse {
  success: boolean
  task_id?: string
  message?: string
  error?: string
  video_url?: string
  status?: 'pending' | 'processing' | 'done' | 'failed'
}

interface VideoStatus {
  status: 'pending' | 'processing' | 'done' | 'failed'
  video_url?: string
  message?: string
  error?: string
}

export const useVideoStore = defineStore('video', {
  state: () => ({
    currentVideo: null as VideoGenerationResponse | null,
    videos: [] as VideoGenerationResponse[],
    isGenerating: false,
    error: null as string | null
  }),

  actions: {
    async generateVideo(params: {
      prompt: string
      duration: number
      firstFrame?: string | null
      lastFrame?: string | null
      resolution?: '720p' | '1080p'
      version?: '3.0' | '3.0_pro'
      backendUrl: string
    }) {
      this.isGenerating = true
      this.error = null

      try {
        // 添加重试机制（Render 免费实例可能需要唤醒）
        let lastError: any = null
        const maxRetries = 3
        const retryDelay = 2000 // 2秒

        for (let attempt = 0; attempt < maxRetries; attempt++) {
          try {
            // 根据分辨率设置宽高
            const resolution = params.resolution || '720p'
            const width = resolution === '1080p' ? 1920 : 1280
            const height = resolution === '1080p' ? 1080 : 720

            const response = await $fetch<VideoGenerationResponse>(
              `${params.backendUrl}/api/v1/video/generate`,
              {
                method: 'POST',
                body: {
                  prompt: params.prompt,
                  duration: params.duration,
                  fps: 24,
                  width: width,
                  height: height,
                  first_frame: params.firstFrame,
                  last_frame: params.lastFrame,
                  seed: null,
                  negative_prompt: null,
                  resolution: resolution,
                  version: params.version || '3.0'
                } as VideoGenerationRequest,
                timeout: 60000 // 60秒超时
              }
            )
            
            // 成功，跳出重试循环
            if (response.success && response.task_id) {
              this.currentVideo = response
              this.videos.unshift(response)
              
              console.log('视频生成任务已提交:', response.task_id)
              
              // 开始轮询状态，完成后触发历史记录刷新
              this.pollVideoStatus(response.task_id, params.backendUrl, () => {
                // 视频生成完成或失败后，触发历史记录刷新事件
                setTimeout(() => {
                  window.dispatchEvent(new CustomEvent('video-status-updated'))
                }, 1000)
              })
              return response
            } else {
              throw new Error(response.message || response.error || '生成失败')
            }
          } catch (error: any) {
            lastError = error
            // 如果是最后一次尝试，抛出错误
            if (attempt === maxRetries - 1) {
              throw error
            }
            // 等待后重试
            await new Promise(resolve => setTimeout(resolve, retryDelay * (attempt + 1)))
          }
        }
        
        // 如果所有重试都失败
        throw lastError || new Error('请求失败')

      } catch (error: any) {
        // 处理不同类型的错误
        let errorMessage = '生成失败，请重试'
        
        if (error.message) {
          errorMessage = error.message
        } else if (error.statusCode === 0 || error.name === 'FetchError') {
          errorMessage = '无法连接到后端服务。Render 免费实例可能需要 50 秒左右唤醒，请稍后重试。'
        } else if (error.statusCode >= 500) {
          errorMessage = '后端服务错误，请稍后重试'
        } else if (error.statusCode === 404) {
          errorMessage = 'API 端点不存在，请检查后端配置'
        }
        
        this.error = errorMessage
        throw new Error(errorMessage)
      } finally {
        this.isGenerating = false
      }
    },

    async pollVideoStatus(taskId: string, backendUrl: string, onComplete?: () => void) {
      const maxAttempts = 60 // 最多轮询 60 次（5分钟）
      let attempts = 0

      const poll = async () => {
        if (attempts >= maxAttempts) {
          this.error = '生成超时，请稍后重试'
          if (onComplete) onComplete()
          return
        }

        try {
          const status = await $fetch<VideoStatus>(
            `${backendUrl}/api/v1/video/status/${taskId}`
          )

          // 处理不同的响应格式
          // 后端返回格式：{ "status": "completed", "video_url": "..." } 或 { "status": "processing", ... }
          const videoStatus = status.status
          const videoUrl = status.video_url

          if (videoStatus === 'completed' && videoUrl) {
            if (this.currentVideo) {
              this.currentVideo.video_url = videoUrl
              this.currentVideo.status = 'done'
            }
            // 视频生成完成，触发历史记录刷新
            if (onComplete) onComplete()
            return
          }

          if (videoStatus === 'failed' || videoStatus === 'error') {
            this.error = status.message || status.error || '生成失败'
            if (onComplete) onComplete()
            return
          }

          // 更新状态为 processing
          if (this.currentVideo) {
            this.currentVideo.status = videoStatus === 'processing' ? 'processing' : 'pending'
          }

          // 继续轮询
          attempts++
          setTimeout(poll, 5000) // 每 5 秒轮询一次
        } catch (error: any) {
          this.error = error.message || '查询状态失败'
          // 即使出错也继续轮询，除非达到最大次数
          attempts++
          if (attempts < maxAttempts) {
            setTimeout(poll, 5000)
          } else if (onComplete) {
            onComplete()
          }
        }
      }

      poll()
    }
  }
})

