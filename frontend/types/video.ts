export interface VideoGenerationRequest {
  prompt: string
  duration: number
  fps?: number
  width?: number
  height?: number
  first_frame?: string | null
  last_frame?: string | null
  seed?: number | null
}

export interface VideoGenerationResponse {
  success: boolean
  task_id?: string
  message?: string
  error?: string
  video_url?: string
  status?: 'pending' | 'processing' | 'done' | 'failed'
}

export interface VideoStatus {
  status: 'pending' | 'processing' | 'done' | 'failed'
  video_url?: string
  message?: string
  error?: string
}


